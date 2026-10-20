#!/home/knight/personal-packages/friends/MCSR/env/bin/python
from persistent import RunResponse, persistent
import requests
import os

USER = "pinchyish"

def get(id: int) -> RunResponse:
    data = requests.get(f"https://mcsrranked.com/api/matches/{id}").json()['data']
    return persistent.cache(RunResponse.project(data))

def suggest_discard(run: RunResponse) -> bool:
    print('\t'.join(run.flatten()))
    print('Do you want to discard this run? (will not appear in the spreadsheet)')
    return input('[y/N] ').upper() == 'Y'

def make_copy(runs: list[RunResponse]) -> str:
    return '<table style="text-align:right;"><tbody>' + "".join(run.tohtml() for run in runs) + '</tbody></table>'

def copy_html_arch(html: str):
    import subprocess
    subprocess.run(['wl-copy', '-t', 'text/html'], input=html)

def copy_html_win(html: str):
    # Windows expects a CF_HTML-formatted payload,
    # not just a raw HTML string.
    import win32clipboard
    fragment = html.encode("utf-8")

    header_template = (
        "Version:0.9\r\n"
        "StartHTML:{:010d}\r\n"
        "EndHTML:{:010d}\r\n"
        "StartFragment:{:010d}\r\n"
        "EndFragment:{:010d}\r\n"
    )

    prefix = "<html><body><!--StartFragment-->"
    suffix = "<!--EndFragment--></body></html>"

    # Offsets in CF_HTML are byte offsets from the start.
    placeholder = header_template.format(0, 0, 0, 0).encode("ascii")
    prefix_bytes = prefix.encode("utf-8")
    suffix_bytes = suffix.encode("utf-8")

    start_html = len(placeholder)
    start_fragment = start_html + len(prefix_bytes)
    end_fragment = start_fragment + len(fragment)
    end_html = end_fragment + len(suffix_bytes)

    header = header_template.format(
        start_html, end_html, start_fragment, end_fragment
    ).encode("ascii")

    payload = header + prefix_bytes + fragment + suffix_bytes

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(
            win32clipboard.RegisterClipboardFormat("HTML Format"),
            payload,
        )
    finally:
        win32clipboard.CloseClipboard()

def copy(runs: list[RunResponse]):
    clip = make_copy(runs)
    if os.name == 'nt': copy_html_win(clip)
    else: copy_html_arch(clip)
    return 

def fetch():
    data = requests.get(f"https://mcsrranked.com/api/users/{USER}/matches").json()['data']
    data = list(filter(lambda run: not persistent.find(run['id']), data))
    if not data: return print("No new runs found")
    new: list[RunResponse] = []
    for run in data[::-1]:
        run = get(run['id'])
        if suggest_discard(run): print(f"Discarded run {persistent.discard(run.id)}")
        new.append(run)
    print('New runs:\n' + '\n'.join('\t'.join(run.flatten()) for run in new))
    if input('Do you want to copy these? [Y/n] ').upper() == 'N': return
    copy(new)

def funchelp():
    print('\n'.join(f'- {function}\t\t{functions[function][0]}' for function in functions))

functions = {'exit': ("This one's easy", lambda:print("Exiting, bye"))}
functions['fetch'] = "Get new data from mcsrranked server", fetch
functions['help'] = "You just used it", funchelp
if __name__ == "__main__":
    command = None
    while command != 'exit':
        command = input("What do you want to do? type help for options\n")
        func = functions.get(command, (None, lambda:print("Command not recognised, try typing help")))
        func[1]()