import React from 'react';
import {Composition} from 'remotion';
import {Huazi} from './Huazi';
import edit from './edit.json';
export const Root:React.FC=()=> <Composition id="Huazi" component={Huazi} width={edit.width} height={edit.height} fps={edit.fps} durationInFrames={Math.max(1, Math.ceil(edit.duration*edit.fps))}/>;
