from PIL import Image
import PIL, tempfile, os, paths, subprocess, logging
from fastapi import FastAPI, BackgroundTasks, UploadFile, HTTPException,Depends
from fastapi.responses import FileResponse
from utils import if_exists_delete
from pathlib import Path
from paths import pngquant_path
from db import get_async_conn, create_tables
from sqlalchemy import text

app=FastAPI()

@app.post("/compress")
async def compress_file(image:UploadFile, background_task:BackgroundTasks,conn=Depends(get_async_conn)):
    
    if not image.filename.endswith(".png"):
        return {"message":"can not compress, file format is not PNG!"}
    if image.size > 10485760:
        return {"message":f"can not compress, file size is bigger than 10 megabytes,yours is {round(image.size/(1024*1024),3)}mb"}
    if len(image.filename)>255:
        return {"message":"can not compress, file name is bigger than 255 symbols(less than 256 required)"}
    
    img=None
    try:
        img=Image.open(image.file)
    except PIL.UnidentifiedImageError:
        if img:
            img.close()
        return {"message":"the file is not a type of an image"}
    
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".png",dir="temporary_pngs") as tmp:
            tmp_path=tmp.name
        img.save(tmp_path)
        tmp_path_compressed=(Path(tmp_path).resolve()).with_name(Path(tmp_path).resolve().stem+"_compressed.png")
        quality_min=80
        
        while quality_min > 40:
            try:
                subprocess.run([str(pngquant_path),f"--quality={quality_min}-90","--output",str(tmp_path_compressed),"--force",str(tmp_path)],check=True)
                break
            except subprocess.CalledProcessError as err:
                if err.returncode == 99:
                    logging.info(f"couldn't process png with quality={quality_min}-90 , going lower if possible...")
                    quality_min-=20
                else:
                    logging.exception("error with pngquant occured")
                    raise HTTPException(status_code=500 , detail="something went wrong on server")
                    
        if quality_min < 40:
            return {"message":"couldn't process your PNG file at acceptable quality(>40,<90)"}
        
    except Exception:
        logging.exception("something went wrong in POST /compress endpoint")
        raise HTTPException(status_code=500,detail="something on server went wrong")
    
    finally:
        if img:
            img.close()
        background_task.add_task(if_exists_delete,tmp_path)
        background_task.add_task(if_exists_delete,tmp_path_compressed)
        
    if os.path.exists(tmp_path_compressed):
        try:
            await conn.execute(text("INSERT INTO compresses (file_name) VALUES (:file_name_)"),{"file_name_":image.filename})
            await conn.commit()
        except Exception:
            logging.exception("something went wrong with insert into compresses")
            raise HTTPException(status_code=500,detail="something on server went wrong")
        return FileResponse(tmp_path_compressed, filename=image.filename)
    else:
        logging.error("couldn't find compressed tmp file")
        raise HTTPException(status_code=500,detail="something on server went wrong")
    

@app.on_event("startup")
async def startup():
    await create_tables()
        
            
    
    # compressed_size=os.path.getsize(tmp_path_compressed)
    # return {"message":f"Your PNG file was compressed by {round((image.size-compressed_size)/(1024*1024),2)} mbytes and file's current size is {round(compressed_size/(1024*1024),2)}mb","download_link":"/compress"}
    
    