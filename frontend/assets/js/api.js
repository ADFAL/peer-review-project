const API = "http://127.0.0.1:8000";

async function getData(url){
  const res = await fetch(API + url);
  return await res.json();
}