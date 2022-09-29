import React from 'react';
import { Typography, Container } from '@mui/material';
import './css/MainPanel.css';

function MainPanel() {
    return (
        <>
            <Container maxWidth="xl">
                <Typography variant="h4" sx={{ mb: 5 }} id='cssload-loader'>
                    人工智慧偵測肝臟
                </Typography>
            </Container>
        </>
    );
}

export default MainPanel;