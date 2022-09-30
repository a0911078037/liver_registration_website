import React, { useState, useEffect } from 'react';
import { Typography, Container, Grid, LinearProgress, CircularProgress, Backdrop, Box, Modal, Fade } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './MainPanel.js';

const ip = process.env.REACT_APP_IP;
const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 900,
    height: 800,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
    scrollX: 'hidden',
    overflowY: 'auto',
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
    const [progress, setProgress] = useState(0);
    const [open, setOpen] = React.useState(false);
    const handleClose = () => setOpen(false);
    const [image_area, setImage_area] = useState([]);
    const [load_circule, setLoad_circule] = useState(false);
    // const [seg_img, setSeg_img] = useState('');

    // get gif img
    // function get_seg_img(name) {
    //     fetch(`http://${ip}:8000/segmentation_pic`, {
    //         method: 'POST',
    //         body: JSON.stringify({
    //             data_name: name
    //         }),
    //         headers: {
    //             'Content-type': 'application/json; charset=UTF-8',
    //         },
    //     })
    //         .then((res) => res.json())
    //         .then((data) => {
    //             setSeg_img(data['img']);
    //             setOpen(true);
    //         })
    // }

    function get_seg_progress() {
        fetch(`http://${ip}:8000/segmentation_process`, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        })
            .then((res) => res.json())
            .then((data) => {
                setProgress(parseInt(data['process']));
            })
    }

    async function get_seg_img(img_len=1){
        let image_list = [];
        setImage_area([]);
        setLoad_circule(true);
        setOpen(true);
        for (let i = 0; i <= img_len; i++) {
            await fetch(`http://${ip}:8000/seg_png?pos=${i}`, {
                method: 'GET',
                headers: {
                    'Content-type': 'application/json; charset=UTF-8',
                },
            }).then((res) => res.json())
                .then((data) => {
                    if (data['success'] === false) {
                        showerror(data['msg']);
                        return;
                    }
                    let image = {
                        'src': data['image'],
                        'i': i
                    }
                    image_list.push(image);
                })
        }
        setLoad_circule(false);
        setload_btn(false);
        setImage_area(image_list);
    }
    function send_segment_requset(name) {
        setload_btn(true);
        var logger_hander = setInterval(get_seg_progress, 1000);
        fetch(`http://${ip}:8000/segmentation`, {
            method: 'POST',
            body: JSON.stringify({
                data_name: name
            }),
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        })
            .then((res) => res.json())
            .then((data) => {
                if (data['success'] === false) {
                    showerror(data['success']);
                    clearInterval(logger_hander);
                    setload_btn(false);
                    return;
                }
                clearInterval(logger_hander);
                showmsg('產生圖片中，請稍等');
                get_seg_img(data['img_len']);
            })
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
                }
                else {
                    setTimeout(check_server_status, 1000);
                }
            })
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
            })


    }, []);
    return (
        <>
            <Container maxWidth="xl">
                <Typography variant="h4" sx={{ mb: 5 }} id='cssload-loader'>
                    肝臟分割
                </Typography>
                <Grid container spacing={2}>
                    <Grid item xs={6}>
                        <center><img src='image/s11.gif' alt='sample_one' /></center>
                    </Grid>
                    <Grid item xs={6}>
                        <center><img src='image/s12.gif' alt='sample_two' /></center>
                    </Grid>
                    <Grid item xs={6}>
                        <center><LoadingButton loading={load_btn} variant="contained" onClick={() => send_segment_requset('s11')}>分割第一個Sample</LoadingButton></center>
                    </Grid>
                    <Grid item xs={6}>
                        <center><LoadingButton loading={load_btn} variant="contained" onClick={() => send_segment_requset('s12')}>分割第二個Sample</LoadingButton></center>
                    </Grid>
                    <Grid item xs sx={{ marginTop: '40px' }}>
                        <center><LinearProgress sx={{ width: '50%' }} value={progress} variant="determinate" /></center>
                    </Grid>
                </Grid>
                <Modal
                    aria-labelledby="transition-modal-title"
                    aria-describedby="transition-modal-description"
                    open={open}
                    onClose={handleClose}
                    closeAfterTransition
                    BackdropComponent={Backdrop}
                    BackdropProps={{
                        timeout: 500,
                    }}
                >
                    <Fade in={open}>
                        <Box sx={style}>
                            <center><Typography id="transition-modal-title" variant="h6" component="h2">
                                肝臟分割結果
                            </Typography>
                            <Fade
                                in={load_circule}
                                style={{
                                    transitionDelay: load_circule ? '800ms' : '0ms',
                                    marginTop: '200px'
                                }}
                                unmountOnExit
                            >
                                <CircularProgress />
                            </Fade>
                            <Grid container spacing={2}>{image_area.map((image) => {
                                return (<Grid item xs={12}><img src={image.src} alt={image.i} width='100%' height='100%'></img></Grid>)
                            })}</Grid>
                               </center>
                        </Box>
                    </Fade>
                </Modal>
            </Container>
        </>
    );
}

export default MainPanel;