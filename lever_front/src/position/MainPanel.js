import React, { useState, useEffect } from 'react';
import { Typography, Container, Grid, Modal, Fade, Box, Backdrop } from '@mui/material';
import { PCDLoader } from 'three/examples/jsm/loaders/PCDLoader';
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { LoadingButton } from '@mui/lab';
import { toast } from 'react-toastify';
import Stats from 'three/addons/libs/stats.module.js';
import * as THREE from 'three';
import './MainPanel.css';

const ip = process.env.REACT_APP_IP;
const img_size = {
    x: 700,
    y: 700,
};

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 900,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
    overflow: 'hidden',
    padding: 0,
    paddingBottom: '30px',
};

function showerror(msg) {
    toast.error(msg, {
        position: "top-center",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        draggable: true,
        progress: undefined,
        theme: 'colored',
        toastId: 'main_toast_error'
    });
}

function showmsg(msg) {
    toast.success(msg,
        {
            position: "top-center",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: true,
            draggable: true,
            progress: undefined,
        }
    )
}

function MainPanel() {
    const [load_btn, setload_btn] = useState(false);
    const [open, setOpen] = React.useState(false);
    const handleClose = () => setOpen(false);
    const params = {
        result: false,
        target: false,
        source: false
    };
    let perspectiveCamera, controls, scene, renderer, stats, color;

    function show_3d(name1, name2) {
        setload_btn(true);
        showmsg('伺服器已經開始處理，請稍待大約一分鐘');
        fetch(`http://${ip}:8000/position`, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
            },
            body: JSON.stringify({
                data_name1: name1,
                data_name2: name2
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data['success'] === false) {
                    showerror(data['msg']);
                    setload_btn(false);
                    return;
                }
            })
            .then(() => {
                showmsg('伺服器處理完畢，正在開啟3D圖片')
                setload_btn(false);
                setOpen(true);
                init();
                animate();
            })

    }

    function init() {
        const aspect = window.innerWidth / window.innerHeight;
        document.getElementById('3d_canvas').innerHTML = '';
        document.getElementById('gui_area').innerHTML = '';
        perspectiveCamera = new THREE.PerspectiveCamera(60, aspect, 1, 1000);
        perspectiveCamera.position.z = 500;
        color = new THREE.Color(0xFFFFFF);
        scene = new THREE.Scene();

        scene.background = color;
        let loader = new PCDLoader();
        loader.load(`http://${ip}:8000/position_file?f=target`, function (points) {

            points.material.size = 3;
            points.geometry.rotateX(Math.PI);
            points.name = 'target';
            points.visible = false;
            scene.add(points);
        });
        loader.load(`http://${ip}:8000/position_file?f=result`, function (points) {

            points.material.size = 3;
            points.geometry.rotateX(Math.PI);
            points.name = 'result';
            points.visible = false;
            scene.add(points);
        });
        loader.load(`http://${ip}:8000/position_file?f=source`, function (points) {

            points.material.size = 3;
            points.geometry.rotateX(Math.PI);
            points.name = 'source';
            scene.add(points);
        });
        const gui = new GUI({ container: document.getElementById('gui_area') });
        gui.add(params, 'source').name('source').setValue(1).onChange(function (value) {
            model_control('source', scene, value);
        });
        gui.add(params, 'target').name('target').onChange(function (value) {
            model_control('target', scene, value);
        });
        gui.add(params, 'result').name('result').onChange(function (value) {
            model_control('result', scene, value);
        });

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(img_size.x, img_size.y, false);
        document.getElementById('3d_canvas').appendChild(renderer.domElement);
        stats = new Stats();
        document.getElementById('3d_canvas').appendChild(stats.dom);

        window.addEventListener('resize', onWindowResize);
        createControls(perspectiveCamera);

    }

    function model_control(model, scene, value) {
        scene.getObjectByName(model).visible = value;
    }

    function createControls(camera) {
        controls = new TrackballControls(camera, renderer.domElement);
        controls.rotateSpeed = 1.5;
        controls.zoomSpeed = 1.2;
        controls.panSpeed = 0.8;
        controls.keys = ['KeyA', 'KeyS', 'KeyD'];
    }

    function onWindowResize() {
        const aspect = img_size.x / img_size.y;
        perspectiveCamera.aspect = aspect;
        perspectiveCamera.updateProjectionMatrix();
        renderer.setSize(img_size.x, img_size.y);
        controls.handleResize();

    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        stats.update();
        render();
    }

    function check_server_status() {
        fetch(`http://${ip}:8000/busy`, {
            method: 'GET',
            header: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        })
            .then((res) => res.json())
            .then((data) => {
                if (data['busy'] === false) {
                    setload_btn(false);
                    showmsg('伺服器處理完成');
                    return true;
                }
                else {
                    setTimeout(check_server_status, 1000);
                }
            }).catch((error)=>{
                setTimeout(check_server_status, 1000);
            })
    }

    function render() {
        renderer.render(scene, perspectiveCamera);
    }

    useEffect(() => {
        fetch(`http://${ip}:8000/busy`, {
            method: 'GET',
            header: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        })
            .then((res) => res.json())
            .then((data) => {
                if (data['busy'] === true) {
                    setload_btn(true);
                    showerror('伺服器正在處理請求中，請稍等');
                    check_server_status();
                }
            }).catch((error)=>{
                showerror('無法連線到伺服器，重試中');
                setload_btn(true);
                check_server_status();
            })
    }, []);

    return (
        <>
            <Container maxWidth="xl">
                <Typography variant="h4" sx={{ mb: 5 }} id='cssload-loader'>
                    肝臟定位
                </Typography>
            </Container>
            <Grid container spacing={2}>
                <Grid item xs={6}>
                    <center><img src='image/s11.gif' alt='sample_one' /></center>
                </Grid>
                <Grid item xs={6}>
                    <center><img src='image/s12.gif' alt='sample_two' /></center>
                </Grid>
                <Grid item xs={12}>
                    <center><LoadingButton loading={load_btn} variant="contained" onClick={()=>show_3d(process.env.REACT_APP_BTN1, process.env.REACT_APP_BTN2)} >計算肝臟位移量</LoadingButton></center>
                </Grid>
            </Grid>

            <Modal
                aria-labelledby="transition-modal-title"
                aria-describedby="transition-modal-description"
                open={open}
                onClose={handleClose}
                closeAfterTransition
                keepMounted
                BackdropComponent={Backdrop}
                BackdropProps={{
                    timeout: 500,
                }}
            >
                <Fade in={open}>
                    <Box sx={style}>
                        <center><div id='gui_area'></div>
                        <Typography id="transition-modal-title" variant="h6" component="h2" sx={{height:'100px', paddingTop:'20px'}}>
                            肝臟定位結果
                            <div>LEFT: 轉動, MIDDLE: 縮放, RIGHT: 位移</div>
                        </Typography>
                           
                            <div id='3d_canvas'></div>    </center>
                    </Box>
                </Fade>
            </Modal>
        </>
    );
}

export default MainPanel;