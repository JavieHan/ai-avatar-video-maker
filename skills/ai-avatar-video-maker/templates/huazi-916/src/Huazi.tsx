// Community base composition. Media and text are supplied by each creator.
import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import editJson from './edit.json';
import timelineJson from './tl.json';

type Segment = {start:number; end:number; text:string; chars?:Record<string,number>};
type Sticker = {start:number; end:number; title:string; tags:string[]};
type Edit = {width:number; height:number; fps:number; duration:number; video:string; voice:string|null; music:string|null; musicVolume:number; badge:string|null; stickers:Sticker[]};
const edit = editJson as Edit;
const segments = timelineJson.segs as Segment[];
const font = '"PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif';
const punctuation = new Set(Array.from('，。、：；！？,.:;!?\n'));
type Line = {text:string; start:number; end:number};

function linesFor(s:Segment):Line[] {
  const chars = Array.from(s.text);
  const parts:{text:string; index:number}[]=[];
  let part=''; let start=0;
  const push=()=>{if(part.trim())parts.push({text:part.trim(),index:start});part='';};
  chars.forEach((ch,index)=>{
    if(punctuation.has(ch)){push();start=index+1;return;}
    if(!part && ch.trim())start=index;
    part+=ch;
    // Do not split a Latin word in the middle.
    if(Array.from(part).length>=14 && !( /[A-Za-z]/.test(ch) && /[A-Za-z]/.test(chars[index+1] || '') )){push();start=index+1;}
  });
  push();
  const at=(index:number)=>{
    const t=s.chars?.[String(index)];
    return typeof t==='number' && Number.isFinite(t) && t>=s.start && t<=s.end ? t : s.start+(s.end-s.start)*index/Math.max(chars.length,1);
  };
  const times=parts.map(p=>at(p.index));
  // Weak ASR timestamps may be non-monotonic; show in script order.
  for(let i=1;i<times.length;i++) times[i]=Math.max(times[i-1],times[i]);
  return parts.map((p,i)=>({text:p.text,start:times[i],end:times[i+1] ?? s.end}));
}
const lines=segments.flatMap(linesFor);

const Captions:React.FC=()=>{
 const f=useCurrentFrame(), {fps,width,height}=useVideoConfig(); const t=f/fps;
 const line=lines.find(l=>t>=l.start && t<l.end);
 if(!line)return null;
 return <div style={{position:'absolute',left:'5%',right:'5%',bottom:'6%',display:'flex',justifyContent:'center',textAlign:'center',fontFamily:font,fontWeight:700,fontSize:Math.min(width*.055,height*.04),lineHeight:1.3,color:'white',textShadow:'-2px -2px 0 #222, 2px -2px 0 #222, -2px 2px 0 #222, 2px 2px 0 #222, 0 3px 8px #000b',whiteSpace:'pre-wrap'}}>{line.text}</div>;
};
const Stickers:React.FC=()=>{
 const f=useCurrentFrame(),{fps,width,height}=useVideoConfig(),t=f/fps;
 const s=edit.stickers.find(x=>t>=x.start && t<x.end);if(!s)return null;
 const fade=Math.max(0,Math.min(1,(t-s.start)/.2,(s.end-t)/.2));
 const size=Math.min(width*.095,height*.075);
 return <div style={{position:'absolute',left:'6%',bottom:'19%',display:'flex',alignItems:'center',gap:size*.16,opacity:fade,fontFamily:font}}>
  <div style={{width:size*1.25,height:size*1.25,borderRadius:size*.24,background:'#ffe4aa',display:'grid',placeItems:'center',transform:'rotate(-5deg)',boxShadow:'0 3px 12px #6c4a2835'}}><svg width="70%" height="70%" viewBox="0 0 70 70" fill="none" stroke="#a6653e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="15" y="10" width="38" height="48" rx="5" fill="#fff9ed"/><path d="M23 23h22M23 31h22M23 39h15"/><path d="M46 48l13-13 4 4-13 13-6 2z" fill="#f6b76c"/></svg></div>
  <div><div style={{fontSize:size*.28,fontWeight:800,color:'#fff',textShadow:'0 2px 5px #493527bb',marginBottom:size*.1}}>{s.title}</div><div style={{display:'flex',gap:size*.06}}>{s.tags.map((tag,i)=><span key={i} style={{fontSize:size*.19,fontWeight:700,color:'#6f4c34',background:i===1?'#ffe3a5':'#fff7e9',padding:`${size*.04}px ${size*.12}px`,borderRadius:size*.07}}>{tag}</span>)}</div></div>
 </div>;
};
export const Huazi:React.FC=()=> <AbsoluteFill style={{backgroundColor:'#000'}}>
 <OffthreadVideo src={staticFile(edit.video)} muted={!!edit.voice} style={{width:'100%',height:'100%',objectFit:'contain'}}/>
 {edit.voice && <Audio src={staticFile(edit.voice)}/>}
 {edit.music && <Audio src={staticFile(edit.music)} volume={edit.musicVolume}/>}
 {edit.badge && <div style={{position:'absolute',top:'2.5%',right:'3.5%',fontFamily:font,fontSize:'1.8em',color:'white',textShadow:'0 2px 5px #000'}}>{edit.badge}</div>}
 <Stickers/>
 <Captions/>
 </AbsoluteFill>;
