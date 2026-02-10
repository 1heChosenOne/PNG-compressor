from pydantic_settings import BaseSettings, SettingsConfigDict

class postgresql_config(BaseSettings):
    DB_ADMIN_USERNAME:str
    DB_PASSWORD:str
    DB_PORT:int
    DB_HOST:str
    DB_NAME:str
    
    @property
    def DB_GET_URL(self):
        return f"postgresql+asyncpg://{self.DB_ADMIN_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        
    model_config=SettingsConfigDict(env_file=".env")
      
db_settings=postgresql_config()
        
        
        