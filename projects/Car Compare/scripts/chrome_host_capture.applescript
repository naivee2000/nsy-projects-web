on run argv
  if (count of argv) is less than 7 then error "Target URL, limits, deadline, and scope reader are required"
  set targetUrl to item 1 of argv
  set maxCharacters to (item 2 of argv) as integer
  set maxClicks to (item 3 of argv) as integer
  set backgroundMode to (item 4 of argv) is not "0"
  set deadlineAt to (item 5 of argv) as real
  set maxPages to (item 6 of argv) as integer
  set scopeReader to item 7 of argv
  if targetUrl does not start with "https://" then error "Only HTTPS URLs are allowed"
  if maxPages < 1 then error "Page budget exhausted"
  my checkDeadline(deadlineAt)

  set probeWindow to missing value
  set previousFrontApp to ""
  if backgroundMode then
    try
      tell application "System Events" to set previousFrontApp to name of first application process whose frontmost is true
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

    set pagesJson to ""
    set beforeSnapshot to "null"
    set clicksMade to 0
    repeat with pageIndex from 1 to maxPages
      my checkDeadline(deadlineAt)
      repeat 6 times
        my checkDeadline(deadlineAt)
        tell application "Google Chrome" to execute probeTab javascript "window.scrollTo(0,document.documentElement.scrollHeight)"
        delay 0.25
      end repeat
      set scopeJson to my waitForScope(probeTab, scopeReader, beforeSnapshot, deadlineAt)
      set captureScript to "(()=>{const snapshot=" & scopeJson & ";const selectors=['a[href*=\"/cars-for-sale/vehicle/\"]','a[href*=\"/cars-for-sale/inventory/\"]','a[href*=\"/inventory/\"]','a[href*=\"/vin/\"]','a[href*=\"listing\"]','a[href*=\"/details/\"]'];const cardMap=new Map();for(const a of document.querySelectorAll(selectors.join(','))){let n=a,t=(a.innerText||a.textContent||'').trim();for(let d=0;d<7&&n;d++,n=n.parentElement){const c=(n.innerText||n.textContent||'').trim();if(c.length>=50&&c.length<=4000&&/(?:\\$\\s*)?[0-9]{2,3},[0-9]{3}/.test(c))t=c;if(/(?:19|20)\\d{2}/.test(t)&&/(?:\\$\\s*)?[0-9]{2,3},[0-9]{3}/.test(t))break}const href=a.href||'';if(href&&/(?:19|20)\\d{2}/.test(t)&&/(?:\\$\\s*)?[0-9]{2,3},[0-9]{3}/.test(t)){const existing=cardMap.get(href);if(!existing||t.length>existing.text.length)cardMap.set(href,{url:href,text:t.slice(0,4000)})}}const latest=" & scopeReader & ";const unchanged=JSON.stringify([latest.controls,latest.fingerprint,latest.busy,latest.document_id])===JSON.stringify([snapshot.controls,snapshot.fingerprint,snapshot.busy,snapshot.document_id]);return JSON.stringify({title:document.title,url:location.href,text:(document.body?.innerText||'').slice(0," & maxCharacters & "),height:document.documentElement.scrollHeight,cards:[...cardMap.values()],scope_snapshot:latest,selected_controls:latest.controls,result_refresh_confirmed:snapshot.result_refresh_confirmed===true&&unchanged})})()"
      tell application "Google Chrome" to set pageJson to execute probeTab javascript captureScript
      if pagesJson is not "" then set pagesJson to pagesJson & ","
      set pagesJson to pagesJson & pageJson
      if pageJson does not contain "\"result_refresh_confirmed\":true" then exit repeat
      if pageIndex is maxPages or clicksMade is greater than or equal to maxClicks then exit repeat
      set beforeSnapshot to scopeJson
      my checkDeadline(deadlineAt)
      set clickScript to "(()=>{const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return !e.disabled&&e.getAttribute('aria-disabled')!=='true'&&s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};const candidates=[...document.querySelectorAll('button,a')].filter(visible).filter(e=>{const label=(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||e.textContent||'').trim();return /^(?:see more results|show more results|load more(?: results)?|next page|go to the next page)$/i.test(label)||e.getAttribute('rel')==='next'||(/^next$/i.test(label)&&/(?:page|pagenumber)=?\\d*/i.test(e.getAttribute('href')||''))});if(!candidates.length)return 'no';candidates[0].click();return 'yes'})()"
      tell application "Google Chrome" to set clicked to execute probeTab javascript clickScript
      if clicked is not "yes" then exit repeat
      set clicksMade to clicksMade + 1
    end repeat

    set backgroundJson to "false"
    if backgroundMode then set backgroundJson to "true"
    set finalScript to "(()=>{const pages=[" & pagesJson & "];const unique=new Map();for(const p of pages)for(const c of p.cards)if(!unique.has(c.url))unique.set(c.url,c);const cards=[];let remaining=" & maxCharacters & "*4;for(const c of unique.values()){if(remaining<=0)break;const text=c.text.slice(0,Math.min(4000,remaining));remaining-=text.length;cards.push({url:c.url,text})}const last=pages.at(-1)||{};return JSON.stringify({title:last.title,url:last.url,text:pages.map(p=>p.text).join('\\n---\\n').slice(0," & maxCharacters & "),cards,pages:pages.map(p=>({...p,text:undefined,cards:p.cards.length,textLength:p.text.length})),pagesExamined:pages.length,cardsExamined:pages.reduce((n,p)=>n+p.cards.length,0),loadMoreClicked:" & clicksMade & ",backgroundMode:" & backgroundJson & ",selected_controls:last.selected_controls||[],result_refresh_confirmed:pages.length>0&&pages.every(p=>p.result_refresh_confirmed),validation_status:'unverified',requires_independent_scope_validation:true})})()"
    my checkDeadline(deadlineAt)
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

on checkDeadline(deadlineAt)
  set nowSeconds to (do shell script "/bin/date +%s") as real
  if nowSeconds is greater than or equal to deadlineAt then error "deadline_exceeded"
end checkDeadline

on waitForScope(probeTab, scopeReader, beforeSnapshot, deadlineAt)
  my checkDeadline(deadlineAt)
  tell application "Google Chrome" to execute probeTab javascript "delete window.__carCompareScopePoll"
  set snapshotJson to "{}"
  repeat 60 times
    my checkDeadline(deadlineAt)
    set pollScript to "(()=>{const s=" & scopeReader & ";const before=" & beforeSnapshot & ";const state=window.__carCompareScopePoll||(window.__carCompareScopePoll={signature:'',refreshed:before===null});if(before&&(s.fingerprint!==before.fingerprint||s.document_id!==before.document_id))state.refreshed=true;const signature=JSON.stringify([s.url,s.controls,s.fingerprint,s.text,s.busy]);const ready=s.ready_state==='complete'&&!s.busy&&(s.result_count>0||/\\b(?:no (?:matching )?(?:vehicles|cars|results|listings)(?: found| available)?|0 (?:matching )?(?:vehicles|cars|results|listings))\\b/i.test(s.text));const confirmed=ready&&state.refreshed&&signature===state.signature;state.signature=s.busy?'':signature;return JSON.stringify({...s,result_refresh_confirmed:confirmed})})()"
    tell application "Google Chrome" to set snapshotJson to execute probeTab javascript pollScript
    if snapshotJson contains "\"result_refresh_confirmed\":true" then return snapshotJson
    delay 0.25
  end repeat
  return snapshotJson
end waitForScope
