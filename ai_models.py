import google.generativeai as genai
import json
import os


genai.configure(api_key="AIzaSyC433X8QaDLDQbTa2BLfZUlzi16RnKzNuk")


class AiModel:
    __generation_config__ = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json"
    }
    
    def __init__(self, instruction_filename, model_name="gemini-1.5-flash",):
        with open(f"./models_instructions/{instruction_filename}") as instruction_file:
            system_instruction = instruction_file.read()

        self.model = genai.GenerativeModel(
            model_name = model_name,
            #model_name="gemini-2.0-flash-exp",
            generation_config = self.__generation_config__,
            system_instruction = system_instruction
        )


class VisionModel(AiModel):
    __instruction_filename__ = "vision_model.txt"

    def __init__(self):
        AiModel.__init__(self, self.__instruction_filename__)

    async def proc_img(self, myfile, prompt = "") -> str:
        result = await self.model.generate_content_async(
            [myfile, "\n\n", prompt]
        )
        return result.text

    async def get_description(self, photo_filename, prompt = ""):
        myfile = genai.upload_file(photo_filename)
        response = await self.proc_img(myfile,prompt)
        return response
    
    async def get_filters(self, photo_filename, prompt = "", filters=""):
        request = {
            "mode": "filters",
            "prompt": prompt,
            "filters": filters
        }
        str_prompt = json.dumps(request)
        myfile = genai.upload_file(photo_filename)
        response = self.model.generate_content(
            [myfile, "\n\n", str_prompt]
        )
        return response
    
    def get_test(self):
        return self.model.generate_content("Explain how AI works").text


class ComparisonModel(AiModel):
    __instruction_filename__ = "comparison_model.txt"

    def __init__(self):
        AiModel.__init__(self, self.__instruction_filename__)

    def upload_multiple_images(self, image_paths):
        file_uris = []
        for image_path in image_paths:
            file = genai.upload_file(image_path)
            file_uris.append(file.uri)

        return file_uris

    async def proc_img(self, item, *files_urls) -> str:
        result = await self.model.generate_content_async(
            [item, *files_urls]
        )
        return result.text

    async def compare_images(self, item, origin_filename, folder_path):
        prompt = f"{item}\n\n"
        files = []
        filenames = []
        files.append(origin_filename)
        filenames.append(origin_filename)
        for f in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, f)):
                file_path = os.path.join(folder_path, f)
                files.append(file_path)
                prompt += f"{file_path}\n"

        files_urls = self.upload_multiple_images(files)
        response = await self.proc_img(prompt, *files_urls)
        print(response)
        return response 