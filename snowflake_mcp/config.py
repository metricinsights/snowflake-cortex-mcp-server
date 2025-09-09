from dataclasses import dataclass, field


@dataclass
class Config:
    account: str = field(default="")
    token: str = field(default="")
    database: str = field(default="")
    schema: str = field(default="")
    agent: str = field(default="")
    defaults: "Config" = field(default=None)

    def __post_init__(self):
        if self.defaults:
            for key, value in self.defaults.__dict__.items():
                if not getattr(self, key):
                    setattr(self, key, value)
