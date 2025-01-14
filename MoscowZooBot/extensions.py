from config import test


def scoring_points(answers):
    count = 0
    animals = ['Кошка', 'Лиса', 'Волк', 'Медведь']

    for answer in answers:
        for question in test:
            if answer in question['answer']:
                count += question['answer'].get(answer)

    if count < 11:
        return animals[0]
    elif 10 < count < 21:
        return animals[1]
    elif 20 < count < 31:
        return animals[2]
    elif count > 30:
        return animals[3]


def animal_photo(animal):
    paths = {
        'Медведь': '.\\photo\\asiatic_black_bear.jpeg',
        'Волк': '.\\photo\\wolf.jpg',
        'Лиса': '.\\photo\\red_fox.jpg',
        'Кошка': '.\\photo\\amur_cat.png',
    }
    return paths.get(animal)
