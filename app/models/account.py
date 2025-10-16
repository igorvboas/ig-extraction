"""
Model de conta do Instagram
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass, field


@dataclass
class Account:
    """
    Representa uma conta do Instagram com seus metadados
    """
    email: str
    username: str
    password: str
    status: str
    created_at: str
    fingerprint: str  # JSON string
    proxy_used: str
    thread_id: int
    
    # Campos de controle interno (não vêm do CSV)
    is_frozen: bool = False
    frozen_until: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    
    def __post_init__(self):
        """Processa campos após inicialização"""
        # Parse do fingerprint JSON
        if isinstance(self.fingerprint, str):
            try:
                self._fingerprint_dict = json.loads(self.fingerprint)
            except json.JSONDecodeError:
                self._fingerprint_dict = {}
        else:
            self._fingerprint_dict = self.fingerprint
    
    @property
    def fingerprint_dict(self) -> Dict:
        """Retorna fingerprint como dicionário"""
        return self._fingerprint_dict
    
    @property
    def proxy_host(self) -> str:
        """Extrai host do proxy"""
        if ':' in self.proxy_used:
            return self.proxy_used.split(':')[0]
        return self.proxy_used
    
    @property
    def proxy_port(self) -> int:
        """Extrai porta do proxy"""
        if ':' in self.proxy_used:
            return int(self.proxy_used.split(':')[1])
        return 80
    
    def is_available(self) -> bool:
        """
        Verifica se a conta está disponível para uso
        
        Returns:
            True se disponível, False caso contrário
        """
        # Verificar status
        if self.status != "success":
            return False
        
        # Verificar se está congelada
        if self.is_frozen:
            if self.frozen_until and datetime.now() >= self.frozen_until:
                # Descongelar automaticamente
                self.unfreeze()
                return True
            return False
        
        return True
    
    def freeze(self, duration_minutes: int = 60, reason: str = None):
        """
        Congela a conta por um período
        
        Args:
            duration_minutes: Duração do congelamento em minutos
            reason: Motivo do congelamento
        """
        self.is_frozen = True
        self.frozen_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.last_error = reason
        
    def unfreeze(self):
        """Descongela a conta"""
        self.is_frozen = False
        self.frozen_until = None
    
    def mark_used(self):
        """Marca que a conta foi usada"""
        self.last_used = datetime.now()
        self.usage_count += 1
    
    def mark_error(self, error_message: str):
        """
        Registra um erro na conta
        
        Args:
            error_message: Mensagem de erro
        """
        self.error_count += 1
        self.last_error = error_message
    
    def get_proxy_url(self, with_protocol: bool = True) -> str:
        """
        Retorna URL completa do proxy
        
        Args:
            with_protocol: Se deve incluir http:// no início
        
        Returns:
            URL do proxy
        """
        proxy_url = self.proxy_used
        if with_protocol and not proxy_url.startswith('http'):
            proxy_url = f"http://{proxy_url}"
        return proxy_url
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'email': self.email,
            'username': self.username,
            'status': self.status,
            'proxy': self.proxy_used,
            'thread_id': self.thread_id,
            'is_frozen': self.is_frozen,
            'frozen_until': self.frozen_until.isoformat() if self.frozen_until else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count,
            'error_count': self.error_count,
            'last_error': self.last_error
        }
    
    def __repr__(self) -> str:
        return f"Account(username={self.username}, available={self.is_available()})"