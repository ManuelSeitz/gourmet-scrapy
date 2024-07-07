# CSS Selectors

## In recipes page

page_numbers = response.css('button.js-page.page::attr(page)').getall()

recipe_links = response.css("article.c-receta-card-static a.c-receta-card-static__container::attr(href)")

## In a recipe page

recipe_name = response.css('h1.m-hero-receta__title.title::text').get().strip()

recipe_time = response.css('span.m-hero-receta__tiempo.paragraph::text').get().strip()

recipe_image = response.css('picture.m-hero-receta__thumbnail img::attr(data-src)').get()

portions = response.css('span.c-ingredientes__portions::text').get()

ingredients_list = response.css('ul.c-ingredientes__list')

ingredient_name = response.css('li.c-ingredientes__ingrediente span:first-child::text').get()

ingredient_quantity = response.css('li.c-ingredientes__ingrediente span:last-child::text').get()

main_preparation_list = response.css('div.c-preparacion ul:first-of-type')

extra_preparation_titles = response.css('div.c-preparacion p strong::text').getall() // Could be one or more for a single recipe

extra_preparation_lists = response.css('div.c-preparacion ul:first-of-type ~ ul') // Could be one or more for a single recipe




