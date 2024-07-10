from re import sub
import scrapy


class ElGourmetSpider(scrapy.Spider):
    name = "elgourmet"
    allowed_domains = ["elgourmet.com"]
    start_urls = ["https://elgourmet.com/recetas"]
    page = 1
    last_page = None

    def parse(self, response):
        if self.last_page is None:
            page_numbers = [
                int(page_num)
                for page_num in response.css("button.js-page.page::attr(page)").getall()
            ]
            self.last_page = max(page_numbers)

        for link in response.css(
            "article.c-receta-card-static a.c-receta-card-static__container::attr(href)"
        ):
            yield response.follow(link.get(), callback=self.parse_recipe)

        self.page += 1
        if self.page <= self.last_page:
            yield response.follow(
                f"https://elgourmet.com/recetas/?recetas-page={self.page}&region=argentina",
                callback=self.parse,
            )

    def parse_recipe(self, response):
        name = response.css("h1.m-hero-receta__title.title::text").get().strip()

        image = response.css(
            "picture.m-hero-receta__thumbnail img::attr(data-src)"
        ).get()

        preparation_time = response.css(
            "span.m-hero-receta__tiempo.paragraph::text"
        ).get()

        if isinstance(preparation_time, str):
            try:
                preparation_time = int(preparation_time.strip().split(" ")[0])
            except ValueError:
                preparation_time = None

        ingredient_sections = []
        ingredients = []
        quantities = []
        ingredients_per_sections = []

        for ingredient_list in response.css("ul.c-ingredientes__list"):
            section_ingredients = []

            section_title = ingredient_list.css(
                "li.c-ingredientes__list-title::text"
            ).get()

            if isinstance(section_title, str):
                section_title = section_title.strip()
            else:
                section_title = ""

            for ingredient in ingredient_list.css("li.c-ingredientes__ingrediente"):
                ingredient_name = (
                    ingredient.css("span:first-child").xpath("string()").get()
                )

                if isinstance(ingredient_name, str):
                    ingredient_name = ingredient_name.strip()

                ingredient_quantity = ingredient.css("span:last-child::text").get()

                if isinstance(ingredient_quantity, str):
                    strip_ingredient_quantity = ingredient_quantity.strip()
                    ingredient_quantity = sub(r"\s{2,}", " ", strip_ingredient_quantity)
                else:
                    ingredient_quantity = ""

                section_ingredients.append(ingredient_name)
                quantities.append(ingredient_quantity)

            ingredient_sections.append(section_title)
            ingredients.extend(section_ingredients)
            ingredients_per_sections.append(len(section_ingredients))

        preparation_sections = []
        steps = []
        steps_per_sections = []

        for i, preparation_element in enumerate(response.css("div.c-preparacion > *")):
            previous_element = None
            section_title = ""
            section_steps = []

            if i > 0:
                previous_element = response.css("div.c-preparacion > *")[i - 1]

            if preparation_element.root.tag == "ul":
                for step_item in preparation_element.css("li"):
                    if step_item.css("::attr(class)").get() == "tit":
                        section_title = step_item.xpath("string()").get().strip()
                        continue

                    step = step_item.xpath("string()").get().strip()
                    section_steps.append(step)
            else:
                continue

            if previous_element is not None and previous_element.root.tag == "p":
                title_text = previous_element.xpath("string()").get()
                section_title = title_text.strip()

            if not section_title and not section_steps:
                continue

            preparation_sections.append(section_title)
            steps.extend(section_steps)
            steps_per_sections.append(len(section_steps))

        yield {
            "name": name,
            "image": image,
            "preparation_time": preparation_time,
            "ingredient_sections": ingredient_sections,
            "ingredients": ingredients,
            "quantities": quantities,
            "total_ingredients": len(ingredients),
            "ingredients_per_sections": ingredients_per_sections,
            "preparation_sections": preparation_sections,
            "steps": steps,
            "total_steps": len(steps),
            "steps_per_sections": steps_per_sections,
            "url": response.url,
        }
