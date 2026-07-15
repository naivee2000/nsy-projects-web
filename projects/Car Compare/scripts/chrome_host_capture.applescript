on run argv
  if (count of argv) is less than 1 then error "Missing target URL"
  set targetUrl to item 1 of argv
  set maxCharacters to 250000
  set maxClicks to 3
  set backgroundMode to true
  if (count of argv) is greater than 1 then set maxCharacters to (item 2 of argv) as integer
  if (count of argv) is greater than 2 then set maxClicks to (item 3 of argv) as integer
  if (count of argv) is greater than 3 and (item 4 of argv) is "0" then set backgroundMode to false
  if targetUrl does not start with "https://" then error "Only HTTPS URLs are allowed"

  set probeWindow to missing value
  set previousFrontApp to ""
  if backgroundMode then
    try
      set previousFrontApp to path to frontmost application as text
    end try
  end if
  try
    tell application "Google Chrome"
      set probeWindow to make new window
      if backgroundMode then set minimized of probeWindow to true
      set probeTab to active tab of probeWindow
      set URL of probeTab to targetUrl
    end tell
    if backgroundMode and previousFrontApp is not "" then
      try
        tell application previousFrontApp to activate
      end try
    end if

    my waitForPage(probeTab, 45)
    tell application "Google Chrome"
      execute probeTab javascript "window.name=JSON.stringify({carCompareCapture:1,pages:[]})"
    end tell

    set clicksMade to 0
    repeat with clickIndex from 0 to maxClicks
      repeat 6 times
        tell application "Google Chrome"
          execute probeTab javascript "window.scrollTo(0,document.documentElement.scrollHeight)"
        end tell
        delay 0.35
      end repeat

      set capturePageScript to "(()=>{let state;try{state=JSON.parse(window.name||'{}')}catch(e){state={}};if(state.carCompareCapture!==1)state={carCompareCapture:1,pages:[]};const body=document.body?document.body.innerText:'';const selectors=['a[href*=\"/cars-for-sale/vehicle/\"]','a[href*=\"/cars-for-sale/inventory/\"]','a[href*=\"/inventory/\"]','a[href*=\"/vin/\"]','a[href*=\"listing\"]','a[href*=\"/details/\"]'];const links=new Set();for(const a of document.querySelectorAll(selectors.join(','))){let n=a,t=(a.innerText||a.textContent||'').trim();for(let d=0;d<7&&n;d++,n=n.parentElement){const c=(n.innerText||n.textContent||'').trim();if(c.length>=50&&c.length<=4000&&/(?:\\$\\s*)?[0-9]{2,3},[0-9]{3}/.test(c))t=c;if(/(?:19|20)\\d{2}/.test(t)&&/(?:\\$\\s*)?[0-9]{2,3},[0-9]{3}/.test(t))break}if(/(?:19|20)\\d{2}/.test(t)&&/(?:\\$\\s*)?[0-9]{2,3},[0-9]{3}/.test(t))links.add(a.href||t)};const page={title:document.title,url:location.href,text:body.slice(0," & maxCharacters & "),height:document.documentElement.scrollHeight,cards:links.size};const previous=state.pages[state.pages.length-1];if(!previous||previous.url!==page.url||previous.text!==page.text)state.pages.push(page);window.name=JSON.stringify(state);return JSON.stringify({blocked:/page unavailable|access denied|verify you are human|security verification|captcha|unusual activity|network restrictions/i.test(document.title+' '+body.slice(0,1200)),url:location.href,length:body.length,height:page.height,cards:page.cards})})()"
      tell application "Google Chrome" to set beforeJson to execute probeTab javascript capturePageScript
      if beforeJson contains "\"blocked\":true" then exit repeat
      if clickIndex is maxClicks then exit repeat

      set clickScript to "(()=>{const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return !e.disabled&&s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};const controls=[...document.querySelectorAll('button,a')].filter(visible);const candidates=controls.filter(e=>{const label=(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||'').trim();const href=e.getAttribute('href')||'';return /^(?:see more results|show more results|load more(?: results)?|next page)$/i.test(label)||e.getAttribute('rel')==='next'||(/^next$/i.test(label)&&/(?:page|pagenumber)=?\\d*/i.test(href))});if(!candidates.length)return JSON.stringify({clicked:false});const e=candidates[0];const label=(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||'').trim();e.click();return JSON.stringify({clicked:true,label,url:location.href})})()"
      tell application "Google Chrome" to set clickJson to execute probeTab javascript clickScript
      if clickJson does not contain "\"clicked\":true" then exit repeat
      set clicksMade to clicksMade + 1
      delay 1
      my waitForPage(probeTab, 20)
    end repeat

    set backgroundJson to "false"
    if backgroundMode then set backgroundJson to "true"
    set finalScript to "(()=>{let state;try{state=JSON.parse(window.name||'{}')}catch(e){state={pages:[]}};const pages=Array.isArray(state.pages)?state.pages:[];const text=pages.map(p=>p.text||'').join('\\n---\\n').slice(0," & maxCharacters & ");const cardsByUrl=pages.reduce((m,p)=>{m[p.url]=Math.max(m[p.url]||0,Number(p.cards)||0);return m},{});return JSON.stringify({title:document.title,url:location.href,readyState:document.readyState,text,height:document.documentElement.scrollHeight,pages:pages.map(p=>({title:p.title,url:p.url,height:p.height,cards:p.cards,textLength:(p.text||'').length})),pagesExamined:pages.length,cardsExamined:Object.values(cardsByUrl).reduce((n,c)=>n+c,0),loadMoreClicked:" & clicksMade & ",backgroundMode:" & backgroundJson & "})})()"
    tell application "Google Chrome"
      set captureJson to execute probeTab javascript finalScript
      close probeWindow
    end tell
    return captureJson
  on error errorMessage number errorNumber
    if probeWindow is not missing value then
      try
        tell application "Google Chrome" to close probeWindow
      end try
    end if
    error errorMessage number errorNumber
  end try
end run

on waitForPage(probeTab, maxSeconds)
  repeat maxSeconds times
    delay 1
    tell application "Google Chrome"
      set readyState to execute probeTab javascript "document.readyState"
      set bodyLength to execute probeTab javascript "document.body ? document.body.innerText.length : 0"
    end tell
    if readyState is "complete" and (bodyLength as integer) is greater than 100 then exit repeat
  end repeat
end waitForPage
