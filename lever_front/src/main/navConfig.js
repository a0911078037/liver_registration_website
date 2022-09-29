// component
import Iconify from '../component/Iconify';

// ----------------------------------------------------------------------

const getIcon = (name) => <Iconify icon={name} width={22} height={22} />;

const navConfig = [
  {
    title: '主頁',
    path: '/main',
    icon: getIcon('raphael:home')
  },
  {
    title: '肝臟偵測',
    path: '/detection',
    icon: getIcon('medical-icon:i-laboratory'),
  },
  {
    title: '肝臟分割',
    path: '/segmentation',
    icon: getIcon('bi:scissors'),
  },
  {
    title: '肝臟定位',
    path: '/position',
    icon: getIcon('bi:headset-vr'),
  }
];

export default navConfig;