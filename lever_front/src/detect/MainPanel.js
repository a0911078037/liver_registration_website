import React, { useEffect, useState } from 'react';
import { Typography, Container, Grid, TextareaAutosize, Modal, Fade, Box, Backdrop, CircularProgress } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import './MainPanel.css';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ip = process.env.REACT_APP_IP;
const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 800,
    height: 700,
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
    const [load_btn, setload_btn] = useState(true);
    const [console_data, setconsole_data] = useState('');
    const [open, setOpen] = React.useState(false);
    const handleClose = () => setOpen(false);
    const [image_area, setImage_area] = useState([]);
    const [load_circule, setLoad_circule] = useState(false);
    const [dicom_btn, setdicom_btn] = useState(true);
    const [dicom_text, setdicom_text] = useState('上傳自訂樣本(dicom)');
    const [mask_btn, set_mask_btn] = useState(true);
    const [mask_btn_load, set_mask_btn_load] = useState(false);
    const [download_btn, setdownload_btn] = useState(true);
    const [mask_btn_text, set_mask_btn_text] = useState('請先上傳dicom樣本');
    let custom = false;

    async function get_image(image_len = 1) {
        let image_list = [];
        setImage_area([]);
        setLoad_circule(true);
        setOpen(true);
        for (let i = 0; i <= image_len; i++) {
            await fetch(`http://${ip}:8000/detect_png?pos=${i}`, {
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
        setdicom_btn(false);
        setdicom_text('上傳自訂樣本(dicom)');
        set_mask_btn(true);
        set_mask_btn_load(false);
        if(custom){
            setdownload_btn(false);
            custom = false;
        }
    }

    function download_file(){
        setdownload_btn(true);
        fetch(`http://${ip}:8000/download/detect`, {
            method: 'POST',
           
        }).then((res)=>res.blob())
        .then((blob)=>{
            const url = window.URL.createObjectURL(
                new Blob([blob]),
              );
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute(
                'download',
                `detect.nii.gz`,
              );
          
              // Append to html link element page
              document.body.appendChild(link);
          
              // Start download
              link.click();
          
              // Clean up and remove the link
              link.parentNode.removeChild(link);
        })
    }

    function scoll_console_buttom() {
        var console = document.getElementById('console');
        console.scrollTop = console.scrollHeight;
    }
    function get_detect_log() {
        fetch(`http://${ip}:8000/detect_log`, {
            method: 'POST',
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        })
            .then((res) => res.json())
            .then((data) => {
                var log_data = '';
                for (let i = 0; i < data['data'].length; i++) {
                    log_data += data['data'][i];
                    log_data += '\n';
                }
                setconsole_data(log_data);
                scoll_console_buttom();
            })
    }
    function send_detect_requset(name) {
        setload_btn(true);
        setconsole_data('');
        var logger_hander = setInterval(get_detect_log, 1000);
        let image_len = 0;
        fetch(`http://${ip}:8000/detect`, {
            method: 'POST',
            body: JSON.stringify({
                data_name: name
            }),
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
            },
        }).then((res) => res.json())
            .then((data) => {
                if (data['success'] === false) {
                    setload_btn(false);
                    setdicom_btn(false);
                    set_mask_btn(true);
                    set_mask_btn_load(false);
                    setdicom_text('上傳自訂樣本(dicom)');
                    set_mask_btn_text('請先上傳dicom樣本');
                    showerror(data['msg']);
                    clearInterval(logger_hander);
                    image_len = -1;
                    return;
                }
                showmsg('偵測完畢，產生圖片中，請稍等');
                clearInterval(logger_hander);
                image_len = data['image_len'];
            })
            .then(() => {
                if (image_len !== -1) {
                    get_image(image_len);
                }
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
                    setdicom_btn(false);
                    showmsg('伺服器處理完成');
                }
                else {
                    setTimeout(check_server_status, 1000);
                }
            })
            .catch((error) => {
                setTimeout(check_server_status, 1000);
            })
    }

    function upload_data_dicom(event) { 
        setload_btn(true);
        const formdata = new FormData();
        formdata.append('file', event.target.files[0]);
        fetch(`http://${ip}:8000/file/detect_dicom`,{
            method: 'POST',
            body: formdata,
        }).then(res=>res.json())
        .then((data)=>{
            event.target.value = ''
            if(data['success']===false){
                showerror(data['msg']);
                setload_btn(false);
            }
            else{
                setdicom_btn(true);
                set_mask_btn(false);
                setdicom_text('上傳完成');
                set_mask_btn_text('請上傳mask樣本');
            }
            
        })
        .catch(err=>{
            console.log(err);
            showerror(err);
            setload_btn(false);
        })

    }

    function upload_data_mask(event) {
        let flag = false;
        custom = true;
        const formdata = new FormData();
        set_mask_btn_load(true);
        formdata.append('file', event.target.files[0]);
        fetch(`http://${ip}:8000/file/detect_mask`,{
            method: 'POST',
            body: formdata,
        }).then(res=>res.json())
        .then((data)=>{
            event.target.value = ''
            if(data['success']===false){
                showerror(data['msg']);
            }
            else{
                showmsg('開始偵測肝臟');
                flag = true;
                console.log('123');
            }
            
        })
        .then(()=>{
            if(flag === true){
                send_detect_requset('detect');
            }
        })
        .catch(err=>{
            console.log(err);
            showerror(err);
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
                    showerror('伺服器正在處理請求中，請稍等');
                    check_server_status();
                }
                else {
                    setload_btn(false);
                    setdicom_btn(false);
                }
            })
            .catch((error) => {
                showerror('無法連線到伺服器，重試中');
                check_server_status();
            })
    }, []);
    return (
        <>
            <Container maxWidth="xl">
                <Typography variant="h4" sx={{ mb: 5 }} id='cssload-loader'>
                    肝臟偵測
                </Typography>
                <Grid container spacing={2}>
                    <Grid item xs={6}>
                        <center><img src='image/s11.gif' alt='sample_one' /></center>
                    </Grid>
                    <Grid item xs={6}>
                        <center><img src='image/s12.gif' alt='sample_two' /></center>
                    </Grid>
                    <Grid item xs={6}>
                        <center><LoadingButton loading={load_btn} variant="contained" onClick={() => send_detect_requset(process.env.REACT_APP_BTN1)}>偵測第一個Sample</LoadingButton></center>
                    </Grid>
                    <Grid item xs={6}>
                        <center><LoadingButton loading={load_btn} variant="contained" onClick={() => send_detect_requset(process.env.REACT_APP_BTN2)}>偵測第二個Sample</LoadingButton></center>
                    </Grid>
                    <Grid item xs sx={{ marginTop: '40px' }}>
                        <center><TextareaAutosize id='console' placeholder='控制台輸出在此' maxRows={15} readOnly defaultValue={console_data} /></center>
                    </Grid>
                </Grid>
                <div id='upload_area'>
                    <LoadingButton disabled={dicom_btn} variant="contained" component="label"sx={{marginBottom:'50px'}}>{dicom_text}
                    <input
                        type={"file"}
                        hidden
                        onChange={(e)=>{upload_data_dicom(e)}}
                    /></LoadingButton>
                    <LoadingButton disabled={mask_btn} variant="contained" component="label" loading={mask_btn_load} sx={{marginBottom:'50px'}}>{mask_btn_text}
                    <input
                        type={"file"}
                        hidden
                        onChange={(e)=>{upload_data_mask(e)}}
                    /></LoadingButton>
                    <LoadingButton disabled={download_btn} variant="contained" component="label" loading={mask_btn_load} onClick={download_file}>{'下載自訂樣本'}</LoadingButton>
                </div>
            </Container>
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
                        <center><Typography id="transition-modal-title" variant="h6" component="h2">
                            肝臟偵測結果
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
                                return (<Grid item xs={6}><img src={image.src} alt={image.i} width='90%' height='90%'></img></Grid>)
                            })}</Grid>  </center>
                    </Box>
                </Fade>
            </Modal>
        </>
    );
}

export default MainPanel;