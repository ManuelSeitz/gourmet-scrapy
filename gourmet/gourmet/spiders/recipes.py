import scrapy


class RecipesSpider(scrapy.Spider):
    name = "recipes"
    allowed_domains = ["elgourmet.com"]
    start_urls = ["https://elgourmet.com/recetas"]
    page = 2
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
            preparation_time = preparation_time.strip()

        ingredients_sections = []

        for ingredient_list in response.css("ul.c-ingredientes__list"):
            ingredients = []

            ingredient_section_title = ingredient_list.css(
                "li.c-ingredientes__list-title::text"
            ).get()

            for ingredient in ingredient_list.css("li.c-ingredientes__ingrediente"):
                ingredient_name = (
                    ingredient.css("span:first-child").xpath("string()").get()
                )
                ingredient_quantity = ingredient.css("span:last-child::text").get()
                ingredients.append(
                    {"name": ingredient_name, "quantity": ingredient_quantity}
                )

            ingredients_sections.append(
                {"title": ingredient_section_title, "ingredients": ingredients}
            )

        preparation_sections = []

        for i, preparation_element in enumerate(response.css("div.c-preparacion > *")):
            previous_element = None
            step_title = None
            steps = []

            if i > 0:
                previous_element = response.css("div.c-preparacion > *")[i - 1]

            if preparation_element.root.tag == "ul":
                for step_item in preparation_element.css("li"):
                    if step_item.css("::attr(class)").get() == "tit":
                        continue
                    step = step_item.xpath("string()").get().strip()
                    steps.append(step)
            else:
                continue

            if previous_element is not None and (
                previous_element.root.tag == "p"
                or previous_element.css("li::attr(class)").get() == "tit"
            ):
                title_text = previous_element.xpath("string()").get()
                step_title = title_text.strip()

            if step_title is None and not steps:
                continue

            preparation_sections.append({"title": step_title, "steps": steps})

        yield {
            "name": name,
            "image": image,
            "preparation_time": preparation_time,
            "ingredients_sections": ingredients_sections,
            "preparation_sections": preparation_sections,
        }
