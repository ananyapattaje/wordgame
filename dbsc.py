from game.models import Word

words = [
    'ABOUT', 'ABOVE', 'ABUSE', 'ACTOR', 'ACUTE',
    'ADMIT', 'ADOPT', 'ADULT', 'AFTER', 'AGAIN',
    'AGENT', 'AGREE', 'AHEAD', 'ALARM', 'ALBUM',
    'ALERT', 'ALIEN', 'ALIGN', 'ALIKE', 'ALIVE'
]

for word in words:
    word_obj, created = Word.objects.get_or_create(word=word)
    if created:
        print(f'Created word: {word}')
    else:
        print(f'Word already exists: {word}')

print(f'Total words in database: {Word.objects.count()}')
exit()