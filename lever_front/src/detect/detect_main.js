import React from 'react';
import SideBar from '../main/SideBar';
import { styled } from '@mui/material/styles';
import MainPanel from './MainPanel';

const APP_BAR_MOBILE = 64;
const APP_BAR_DESKTOP = 92;

const RootStyle = styled('div')({
    display: 'flex',
    minHeight: '100%',
    overflow: 'hidden'
});

const MainStyle = styled('div')(({ theme }) => ({
    flexGrow: 1,
    overflow: 'auto',
    minHeight: '100%',
    paddingTop: APP_BAR_MOBILE + 24,
    paddingBottom: theme.spacing(10),
    [theme.breakpoints.up('lg')]: {
        paddingTop: APP_BAR_DESKTOP + 24,
        paddingLeft: theme.spacing(2),
        paddingRight: theme.spacing(2)
    }
}));

function Detect_Main() {

    return (
        <RootStyle>
            <SideBar />
            <MainStyle>
                <MainPanel />
            </MainStyle>
        </RootStyle>
    );

}

export default Detect_Main;