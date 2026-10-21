const left = document.getElementById("left")
const content = document.getElementById("content")
const fetchButton = document.getElementById("fetchButton")
const copyButton = document.getElementById("copyButton")
const infoDiv = document.getElementById("info")
async function getHtml(start=null, end=null){
    const response = await fetch(`/html?${start ? 'start='+start : ''}&${end ? 'end='+end : ''}`);
    if(!response.ok)throw Error("Couldn't generate a spreadsheet!");
    return await response.text();
}
fetchButton.addEventListener('click', async (ev) => {
    try{
        await fetchNew();
    }catch(e){
        addMessage(e.message, false);
    }
})
function display(html){
    content.innerHTML = html;
    left.innerHTML = '';
    [...content.getElementsByTagName('tr')].forEach(row => {
        const indicator = document.createElement('div');
        indicator.style.height = `${row.clientHeight}px`;
        left.appendChild(indicator);

    })
}
async function fetchNew(){
    const response = await fetch('/fetch');
    if(!response.ok)throw Error("Couldn't fetch from mcsrranked.com!");
    const newRuns = await response.json()
    if(newRuns.length){
        display(await getHtml());
        addMessage("Update fetched!");
    }else addMessage("No new runs found!", false);
}

getHtml().then(display);

function addMessage(message, good=true){
    const messageDiv = document.createElement('div');
    messageDiv.innerText = message;
    if(!good)messageDiv.classList.add('bad');
    infoDiv.appendChild(messageDiv);
}

copyButton.addEventListener('click', async (ev) => {
    let first = null;
    let last = null;
    [...left.children].forEach((indicator, index) => {
        if(indicator.classList.contains('selected')){
            if(!first)first = index;
            last = index+1;
        }
    });
    await navigator.clipboard.write([new ClipboardItem({["text/html"]: getHtml(first, last)})]);
})


let isDragging = false;
let startRow = null;
let first = null;
let last = null;

function getRow(event) {
    const row = event.target.closest("tr");
    return row && content.contains(row) && row.parentElement.tagName === "TBODY" ? row : null;
}

function selectRows(fromRow, toRow) {
    const rows = [...content.getElementsByTagName('tr')];
    const start = rows.indexOf(fromRow);
    const end = rows.indexOf(toRow);
    if (start === -1 || end === -1) return;
    const first = Math.min(start, end);
    const last = Math.max(start, end);

    const indicators = [...left.getElementsByTagName('div')];
    for(let index=0;index<rows.length;index++){
        indicators[index].classList.toggle("selected", first <= index && index <= last);
    }return [first, last];
}

content.addEventListener("mousedown", event => {
    if (event.button !== 0) return;
    const row = getRow(event);
    event.preventDefault();
    if (!row) return;
    isDragging = true;
    startRow = row;
    selectRows(startRow, row);
});

content.addEventListener("mouseover", event => {
    if (!isDragging || !startRow) return;
    const row = getRow(event);
    if(row)selectRows(startRow, row);
});

document.addEventListener("mouseup", event => {
    startRow = null;
    isDragging = false;
});


addMessage("Press fetch to get new runs from mcsrranked api")
addMessage("Select a few rows and press copy to put them in your clipboard")
addMessage("When rows are copied you can just do ctrl+v in the google spreadsheet to paste")