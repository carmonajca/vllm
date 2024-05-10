from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="server.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Item(BaseModel):
    uuid: Optional[str] = None

    # Environment Information
    provider: Optional[str] = None
    num_cpu: Optional[int] = None
    cpu_type: Optional[str] = None
    cpu_family_model_stepping: Optional[str] = None
    total_memory: Optional[int] = None
    architecture: Optional[str] = None
    platform: Optional[str] = None
    gpu_count: Optional[int] = None
    gpu_type: Optional[str] = None
    gpu_memory_per_device: Optional[int] = None

    # vLLM Information
    model_architecture: Optional[str] = None
    vllm_version: Optional[str] = None
    context: Optional[str] = None

    # Metadata
    log_time: Optional[int] = None
    source: Optional[str] = None


app = FastAPI()


@app.post("/use/")
async def create_item(item: Item):
    logging.info(item.json())
    return {"message": "Item received", "item": item}


# Punto de entrada principal
if __name__ == "__main__":
    uvicorn.run("use_server:app", host="0.0.0.0", port=8800, reload=True)
