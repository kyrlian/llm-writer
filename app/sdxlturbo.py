from datetime import datetime
from diffusers import AutoPipelineForText2Image
import torch

# pip install -r requirements-sdxlturbo.txt --upgrade
# pip install -r requirements-torch-windows-cuda12.txt --upgrade

class sdxlturboPipeline:
    # https://huggingface.co/stabilityai/sdxl-turbo
    def __init__(self, model_id="stabilityai/sdxl-turbo"):
        xlturbopipeline = AutoPipelineForText2Image.from_pretrained(
            model_id, torch_dtype=torch.float16, variant="fp16"
        )
        xlturbopipeline.to("cuda")
        self.pipe = xlturbopipeline

    def generate(self, prompt1):
        image = self.pipe(prompt=prompt1, guidance_scale=0.0).images[0]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = f"outputs/image-{timestamp}.png"
        image.save(fname)
        return image


if __name__ == "__main__":
    pipe = sdxlturboPipeline()
    pipe.generate("un chat dans un bocal")
