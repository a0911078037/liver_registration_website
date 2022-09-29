import React, { useEffect } from 'react';
import { Drawer, Box, Typography, Stack, Button, Container, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import navConfig from './navConfig';
import NavSection from '../component/NavSection';
import Scrollbar from '../component/Scrollbar';
import './css/SideBar.css';

function SideBar() {
    const [contact, setContact] = React.useState(false);
    const SIDEBAR_WIDTH = 280;
    const Content = (
        <Scrollbar
            sx={{
                height: 1,
                '& .simplebar-content': { height: 1, display: 'flex', flexDirection: 'column' },
            }}
        >
            <Container sx={{marginTop:'140px'}}>
                <div className="cssload-tetrominos">
                    <div className="cssload-tetromino cssload-box1"></div>
                    <div className="cssload-tetromino cssload-box2"></div>
                    <div className="cssload-tetromino cssload-box3"></div>
                    <div className="cssload-tetromino cssload-box4"></div>
                </div>
            </Container>
            <Box sx={{ textAlign: 'center', mt: 40, marginTop:'140px' }}>
                <NavSection navConfig={navConfig} />
            </Box>
            <Box sx={{ px: 2.5, pb: 3, mt: 25 }}>
                <Stack alignItems="center" spacing={3} sx={{ pt: 5, borderRadius: 2, position: 'relative' }}>
                    <Box
                        component="img"
                        src="/image/contact.jpg"
                        sx={{ width: 100, position: 'absolute', top: -50 }}
                    />

                    <Box sx={{ textAlign: 'center' }}>
                        <Typography gutterBottom variant="h6">
                            Dev. By 潘威信 陳俊維
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                            AI with tensorflow
                        </Typography>
                    </Box>

                    <Button variant="contained" onClick={setContact}>
                        聯絡我們
                    </Button>
                </Stack>
            </Box>
        </Scrollbar>
    );
    return (
        <div>
            <Drawer
                open
                variant='persistent'
                PaperProps={{
                    sx: {
                        width: SIDEBAR_WIDTH,
                        bgcolor: 'background.default',
                        borderRightStyle: 'dashed',
                    },
                }}
            >
                {Content}
            </Drawer>
            <Dialog open={contact} onClose={()=> setContact(false)}>
                <DialogTitle>聯絡我們</DialogTitle>
                <DialogContent>
                    潘威信 <br/>s1082027@mail.yzu.edu.tw<br/>
                    <hr/>
                    陳俊維 <br/>s1081421@mail.yzu.edu.tw<br/>
                </DialogContent>
                <DialogActions>
                <Button onClick={() => setContact(false)}>關閉</Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}

export default SideBar;