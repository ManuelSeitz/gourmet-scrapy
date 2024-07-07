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

        ingredients = []

        for ingredient in response.css("ul.c-ingredientes__list"):
            ingredient_name = ingredient.css(
                "li.c-ingredientes__ingrediente span:first-child::text"
            ).get()

            if ingredient_name is None:
                continue

            ingredient_name = ingredient_name.strip()

            quantity = ingredient.css(
                "li.c-ingredientes__ingrediente span:last-child::text"
            ).get()

            if isinstance(quantity, str):
                quantity = quantity.strip()

            ingredients.append(
                {
                    "name": ingredient_name,
                    "quantity": quantity,
                }
            )

        main_preparation = []

        for list_item in response.css("div.c-preparacion ul:first-of-type li::text"):
            step = list_item.get()
            main_preparation.append(step)

        extra_preparations_titles = response.css(
            "div.c-preparacion p strong::text"
        ).getall()

        extra_preparations = []

        for i, extra_preparation_list in enumerate(
            response.css("div.c-preparacion ul:first-of-type ~ ul")
        ):
            extra_preparation = []
            for preparation_item in extra_preparation_list.css("li::text"):
                step = preparation_item.get()
                extra_preparation.append(step)
            extra_preparations.append(
                {
                    "title": extra_preparations_titles[i],
                    "preparation": extra_preparation,
                }
            )

        yield {
            "name": name,
            "image": image,
            "preparation_time": preparation_time,
            "ingredients": ingredients,
            "main_preparation": main_preparation,
            "extra_preparations": extra_preparations,
        }
