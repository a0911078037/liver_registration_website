import React from 'react';
import ReactDOM from 'react-dom/client';
import reportWebVitals from './reportWebVitals';
import { Route, BrowserRouter, Routes } from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import Main from './main/main.js'
import Detect_Main from './detect/detect_main';
import Position_Main from './position/position_main';
import Segmentation_Main from './segmentation/segmentation_main';
import Not_Found from './not_found/Not_Found';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastContainer/>
      <Routes>
        <Route path='/' element={<Main />} />
        <Route index path='main' element={<Main />} />
        <Route path='detection' element={<Detect_Main />} />
        <Route path='position' element={<Position_Main />} />
        <Route path='segmentation' element={<Segmentation_Main />} />
        <Route path='*' element={<Not_Found/>}/>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
