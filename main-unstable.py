from manga_ocr import MangaOcr
import openai
import os

temp_folder = 'temp'
openai.api_key = ''

results = []
# messgaes
messages = []

#personality
system_msg = "You are a translator who specialises in translating from japanese to english. you will recieve japanese characters, and you will translate it from japanese to english. You will look at your translation, and if it does not make sense, re-word it so that it makes sense, with nothing extra added in."
messages.append({"role": "system", "content": system_msg})


mocr = MangaOcr()

def process_file(file_path):
    text = mocr(file_path)
    messages.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    results.append(f"{os.path.basename(file_path)}: {reply}")

def custom_sort(item):
    # Extract the 'number_#', 'yes' part from the string
    number_part = item.split(': ')[0]
    # Extract the numeric value from the 'number_' string
    numeric_value = int(number_part.split('_')[1].split('.')[0])
    return numeric_value

def main():
    # Loop through all files in the 'temp' folder
    for file_name in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file_name)

        # Check if the item is a file (not a directory)
        if os.path.isfile(file_path):
            process_file(file_path)

    sorted_list = sorted(results, key=custom_sort)

    for i in sorted_list:
        print(i)

if __name__ == "__main__":
    main()