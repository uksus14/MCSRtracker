from dataclasses import dataclass, asdict, fields
from collections.abc import Generator
from datetime import datetime
from typing import Any, Self
from pathlib import Path
import requests
import json

USER = "pinchyish"

def project(cls: type, data: dict[str, Any]) -> dict[str, Any]:
    return {field.name: data[field.name] for field in fields(cls)}

@dataclass
class SplitResponse:
    time: int
    type: str
    def format(self) -> str:
        minutes, seconds = divmod(self.time//1000, 60)
        return f"{minutes}.{seconds:0>2}"
    @classmethod
    def project(cls, data: dict[str, int|str]) -> Self:
        return cls(**project(cls, data))
    @classmethod
    def find_format(cls, splits: list[Self], name: str) -> str:
        for split in splits:
            if split.type == name: return split.format()
        return 'x'

@dataclass
class RunResponse:
    id: int
    result: dict[str, int]
    forfeited: bool
    timelines: list[SplitResponse]
    date: int
    seedType: str
    bastionType: str
    @classmethod
    def create(cls, **kwargs) -> Self:
        kwargs['timelines'] = [SplitResponse(**split) for split in kwargs['timelines']]
        return cls(**kwargs)
    @classmethod
    def format_enum(cls, enum: str) -> str:
        return enum.replace('_', ' ').title()
    @classmethod
    def project(cls, data: dict[str, Any]) -> Self:
        ans = project(cls, data)
        ans['timelines'] = [SplitResponse.project(split) for split in data['timelines']]
        return cls(**ans)
    def flatten(self) -> Generator[str, None, None]:
        yield datetime.fromtimestamp(self.date).strftime("%d/%m")
        final_time = 'x' if self.forfeited else SplitResponse(self.result['time'], 'finish').format()
        yield final_time
        yield self.format_enum(self.seedType)
        yield self.format_enum(self.bastionType)
        yield 'N/A' if self.forfeited else 'idk'
        for split_name in "story.enter_the_nether nether.find_bastion nether.find_fortress nether.obtain_blaze_rod projectelo.timeline.blind_travel story.follow_ender_eye story.enter_the_end".split():
            yield SplitResponse.find_format(self.timelines, split_name)
        yield final_time
    def tohtml(self) -> str:
        return f'<tr style="background-color:#{"f4cccc" if self.forfeited else "d9ead3"};"><td>' + '</td><td>'.join(self.flatten()) + '</td><td></td></tr>'
    def dumps(self) -> str: return json.dumps(asdict(self), indent=4)

@dataclass
class Persistent:
    caches: list[RunResponse]
    discarded: list[int]
    @property
    def runs(self) -> list[RunResponse]:
        return sorted([run for run in self.caches if run.id not in self.discarded], key=lambda run:run.date)
    def find(self, id: int) -> RunResponse|None:
        return next((run for run in self.caches if run.id == id), None)
    def _add_and_dump[T](self, l: list[T], el: T) -> T:
        l.append(el)
        self.dump()
        return el
    def cache(self, run: RunResponse) -> RunResponse:
        if SplitResponse.find_format(run.timelines, 'story.enter_the_nether') == 'x':
            self.discard(run.id)
        return self._add_and_dump(self.caches, run)
    def discard(self, id: int) -> int: return self._add_and_dump(self.discarded, id)
    @classmethod
    def load(cls) -> Self: return cls.loads(FILE.read_text())
    @classmethod
    def loads(cls, data: dict[str, list[Any]]|str) -> Self:
        if isinstance(data, str): data: dict[str, list[Any]] = json.loads(data)
        return cls(caches=[RunResponse.create(**run) for run in data['caches']], discarded=data['discarded'])
    def dump(self): return FILE.write_text(self.dumps())
    def dumps(self) -> str: return json.dumps(asdict(self), indent=4)
    @staticmethod
    def get(id: int) -> RunResponse:
        data = requests.get(f"https://mcsrranked.com/api/matches/{id}").json()['data']
        return persistent.cache(RunResponse.project(data))
    def fetch(self):
        data = requests.get(f"https://mcsrranked.com/api/users/{USER}/matches?count=70").json()['data']
        return [Persistent.get(run['id']) for run in data[::-1] if not persistent.find(run['id'])]

persistent: Persistent = Persistent(caches=[], discarded=[])
default_content = persistent.dumps().encode()
FILE = Path(__file__).parent / 'persistent.json'
if not FILE.exists() or len(FILE.read_bytes()) <= len(default_content):
    with open(FILE, 'wb') as f:
        f.write(default_content)

persistent = Persistent.load()
