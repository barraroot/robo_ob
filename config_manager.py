import json
import os
from hashlib import sha256

class ConfigManager:
    _instance = None
    _config = None
    _config_path = "config.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Carrega o arquivo de configuração ou cria um padrão se não existir"""
        try:
            if not os.path.exists(self._config_path):
                self._create_default_config()
            
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
                
            if 'tenantID' not in self._config:
                self._generate_tenant_id()
                
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Cria um arquivo de configuração padrão"""
        self._config = {
                "token": "e861165d-8573-484e-bd51-20109a27fd9f",
                "api": "https://backoffice.fybrokers.online/api/v1/",
                "site": "https://fybrokers.online"
        }
        self._save_config()
    
    def _generate_tenant_id(self):
        """Gera um novo tenantID como hash"""
        self._config['tenantID'] = self._generate_hash()
        self._save_config()
    
    @staticmethod
    def _generate_hash():
        """Gera um hash SHA-256 único"""
        import uuid
        return sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def _save_config(self):
        """Salva o arquivo de configuração"""
        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=4, ensure_ascii=False)
    
    def set_config(self, key, value, auto_save=True):
        """
        Adiciona ou atualiza uma propriedade de configuração
        
        Parâmetros:
        - key: Chave no formato 'nivel1.nivel2.propriedade'
        - value: Valor a ser armazenado
        - auto_save: Se True, salva automaticamente no arquivo
        """
        try:
            keys = key.split('.')
            current_level = self._config
            
            for k in keys[:-1]:
                if k not in current_level:
                    current_level[k] = {}
                current_level = current_level[k]
            
            current_level[keys[-1]] = value
            
            if auto_save:
                self._save_config()
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar configuração: {e}")
            return False
    
    @property
    def tenant_id(self):
        """Retorna o tenantID"""
        return self._config.get('tenantID')
    
    @property
    def config(self):
        """Retorna toda a configuração"""
        return self._config
    
    def get(self, key, default=None):
        """Obtém um valor de configuração"""
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

# Variável global para acesso fácil
app_config = ConfigManager()