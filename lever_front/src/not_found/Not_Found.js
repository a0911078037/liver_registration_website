import { Link as RouterLink } from 'react-router-dom';
// @mui
import { styled } from '@mui/material/styles';
import { Button, Typography, Container, Box } from '@mui/material';


// ----------------------------------------------------------------------

const ContentStyle = styled('div')(({ theme }) => ({
    maxWidth: 480,
    margin: 'auto',
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    flexDirection: 'column',
    padding: theme.spacing(12, 0)
}));

// ----------------------------------------------------------------------

export default function Not_Found() {
    return (
        <Container>
            <ContentStyle sx={{ textAlign: 'center', alignItems: 'center' }}>
                <Typography variant="h3" paragraph>
                    該頁面無效
                </Typography>

                <Typography sx={{ color: 'text.secondary' }}>
                    不好意思，我們找不到您的網址路徑，也許您拼錯了路徑?請再確認您的網址路徑
                </Typography>

                <Box
                    component="img"
                    src="/image/contact.jpg"
                    sx={{ height: 260, mx: 'auto', my: { xs: 5, sm: 10 } }}
                />

                <Button to="/main" size="large" variant="contained" component={RouterLink}>
                    回到主頁
                </Button>
            </ContentStyle>
        </Container>

    );
}