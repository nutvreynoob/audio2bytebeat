import os
import numpy as np
import pydub
def aread(f, normalized=False):
    """MP3 to numpy array"""
    a = pydub.AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y

def awrite(f, sr, x, normalized=False):
    """numpy array to MP3"""
    channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
    if normalized:  # normalized array - each item should be a float in [-1, 1)
        y = np.int16(x * 2 ** 15)
    else:
        y = np.int16(x)
    song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
    song.export(f, format="mp3", bitrate="320k")
def getCharacterHex(a):
    a=hex(a&0xffff).split("x")[1]
    while not len(a) in [2,4]:
        a="0"+a
    if len(a)==2:
        return "\\x"+a
    else:
        return "\\u"+a
def getRepeatString(a,rep):
    a=chs[a]
    if a=="\n":
        print("tried to repeat newline")
        a="\\n"
    if a=="\x0d":
        print("tried to repeat r")
        a="\\r"
    return '${r(`'+a+'`,'+str(rep)+')}'
def toAdd(a,rep):
    if rep==1 or len(getRepeatString(a,rep))>len(chs[a])*rep:
        return chs[a]*rep
    else:
        return getRepeatString(a,rep)
def sizeStr(s):
    return (str(s) if s<1000 else str(int(s/1000))+"k")

chs=[(chr(a) if (a>0x1f and a<0x7f) or (a>0xa0) else getCharacterHex(a)) for a in range(0,256)]
chs[92]="\\\\"
chs[96]="\\`"
final=""
loop=input("make audio loop? (y/n)")=="y"
samplerate=int(input("sample rate? (Hz)"))
print("formatted - \\x69, \\x00");
print("mixed     - E, \\x00");
print("special   - E, NUL");
format = input("format type? (f/m/s)")
if format=="f":
    chs=[getCharacterHex(a) for a in range(0,256)]
if format=="s":
    chs=[chr(a) for a in range(0,256)]
    chs[92]="\\\\"
    chs[96]="\\`"
    chs[10]="\\n"
    chs[13]="\\r"

os.system("del temp.mp3")
os.system("ffmpeg -i "+input("enter mp3 file: ")+" -ac 1 -ar "+str(samplerate)+" temp.mp3")
sr,vals=aread("temp.mp3",normalized=True)
vals=list(vals)
rep=0
bef=int(((vals[0]+1)/2)*255)
for vi in range(0,len(vals)):
    rep+=1
    val=vals[vi]
    v=((val+1)/2)*255
    if bef!=int(v):
        bef=int(v)
        final+=toAdd(int(v),rep)
        rep=0
    try:
        print("sample "+str(vi)+"/"+str(len(vals))+" ("+str(vi/len(vals)*100)[0:8]+"%), compress "+str(100/((len(final)/((vi+1)/len(vals)))/len(vals)))[0:8]+"% size "+sizeStr(len(final))+" est. "+sizeStr(int(len(final)/((vi+1)/len(vals)))),end="\r")
    except:
        print("Failed to summarize action.")
if loop:
    final="z=0,r=(b,c)=>b.repeat(c),a=`"+final+"`;return ((t,sr)=>{z+=((a.charCodeAt((t*"+str(samplerate)+")%a.length)/(255/2)-1)-z)/Math.max(sr/"+str(samplerate)+",1);if(!z){z=0};return z})"
else:
    final="z=0,r=(b,c)=>b.repeat(c),a=`"+final+"`;return ((t,sr)=>{z+=(((t*"+str(samplerate)+"<a.length?a.charCodeAt(t*"+str(samplerate)+")/(255/2)-1:0))-z)/Math.max(sr/"+str(samplerate)+",1);if(!z){z=0};return z})"
f=open("output.txt","w", encoding="utf-8")
f.write(final)
f.close()
print("\nOutput written in output.txt")
os.system("del temp.mp3")