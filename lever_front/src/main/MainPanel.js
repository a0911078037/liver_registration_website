import React from 'react';
import { Typography, Container, Grid } from '@mui/material';
import './css/MainPanel.css';
import Iconify from '../component/Iconify';

function MainPanel() {
    return (
        <>
            <Container maxWidth="xl">
                <Typography variant="h4" sx={{ mb: 5 }} id='cssload-loader'>
                    肝臟定位Ai輔助診斷系統
                </Typography>
                <Grid container rowSpacing={5} sx={{marginLeft:'150px', paddingTop:'30px'}}>
                    <Grid item xs={12}>
                    <Iconify icon={'mdi:account'} width={22} height={22} />;
                    <Typography variant="h4" sx={{ mb: 5 }} id='des'>
                        動機目的
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 5 }} id='des'>
                        近年來新冠疫情肆虐，造成全世界醫療系統的龐大負擔，台灣的醫療量能也在逐漸上升的每日確診人數逐漸崩潰。
                        身為一個資訊工程系的大學生，我也想為了自己的家園貢獻一份心力，因此製作出一個預測模型來幫助醫師診斷進而減少病人診斷時間。
                        藉由核磁共振產出的CT影像，訓練出肝臟定位的模型讓醫師能快速追蹤前後一次CT影像中腫瘤的位置以幫助診斷。
                    </Typography>
                    </Grid>

                    <Grid item xs={12}>
                    <Iconify icon={'ant-design:star-filled'} width={22} height={22} />;
                    <Typography variant="h4" sx={{ mb: 5 }} id='des'>
                        作品特色
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 5 }} id='des'>
                        肝臟定位Ai輔助診斷系統，最主要的功能是肝臟定位協助腫瘤追蹤診斷，而實作的方法切割成主要三項，分別是肝臟偵測、肝臟分割、肝臟定位，再藉由網頁的方式呈現。
                    </Typography>
                    </Grid>

                    <Grid item xs={12}>
                    <Iconify icon={'ant-design:question-circle-outlined'} width={22} height={22} />;
                    <Typography variant="h4" sx={{ mb: 5 }} id='des'>
                        如何使用
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 5 }} id='des'>
                        點選左邊的操作選單，可進入對應的功能。後端已經內建測試資料，不須額外上傳資料即可使用。也能上傳額外資料來觀看結果。詳細說明請查看企畫書。
                    </Typography>
                    </Grid>
                    
                </Grid>
               
            </Container>
        </>
    );
}

export default MainPanel;