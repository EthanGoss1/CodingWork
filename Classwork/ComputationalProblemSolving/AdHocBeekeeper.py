def find_favorite_word(words):
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    favorite_word = ""
    max_double_vowels = 0

    for word in words:
        count = 0
        i = 0
        while i < len(word) - 1:
            if word[i] == word[i + 1] and word[i] in vowels:
                count += 1
                i += 2  # Skip the next letter for speed
            else:
                i += 1
        if count >= max_double_vowels:
            max_double_vowels = count
            favorite_word = word
    return favorite_word


if __name__ == "__main__":
    output_list = []
    while True:
        amt_of_words = int(input())
        if amt_of_words == 0:
            break
        words = [input().strip() for i in range(amt_of_words)]
        output_list.append(find_favorite_word(words))
    for i in output_list:
        print(i)