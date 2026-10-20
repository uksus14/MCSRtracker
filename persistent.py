from collections.abc import Generator
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from typing import Any, Self
from pathlib import Path
import json

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
        return '<tr style="background-color:#f4cccc;"><td>' + '</td><td>'.join(self.flatten()) + '</td></tr>'

@dataclass
class Persistent:
    caches: list[RunResponse]
    discarded: list[int]
    def find(self, id: int) -> RunResponse|None:
        for run in persistent.caches:
            if run.id == id: return run
        return None
    def _add_and_dump[T](self, l: list[T], el: T) -> T:
        l.append(el)
        self.dump()
        return el
    def cache(self, run: RunResponse) -> RunResponse: return self._add_and_dump(self.caches, run)
    def discard(self, id: int) -> int: return self._add_and_dump(self.discarded, id)
    @classmethod
    def load(cls) -> Self: return cls.loads(FILE.read_text())
    @classmethod
    def loads(cls, data: dict[str, list[Any]]|str) -> Self:
        if isinstance(data, str): data: dict[str, list[Any]] = json.loads(data)
        return cls(caches=[RunResponse(**run) for run in data['caches']], discarded=data['discarded'])
    def dump(self): return FILE.write_text(self.dumps())
    def dumps(self) -> str: return json.dumps(asdict(self), indent=4)


persistent: Persistent = Persistent(caches=[], discarded=[])
default_content = persistent.dumps().encode()
FILE = Path(__file__).parent / 'persistent.json'
if not FILE.exists() or len(FILE.read_bytes()) <= len(default_content):
    with open(FILE, 'wb') as f:
        f.write(default_content)

persistent = Persistent.load()
