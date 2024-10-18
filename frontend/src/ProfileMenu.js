import React, { useState } from 'react';
import { useKeycloak } from '@react-keycloak/web';
import {
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Typography,
  Divider,
} from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

function ProfileMenu() {
  const { keycloak } = useKeycloak();
  const [anchorEl, setAnchorEl] = useState(null);

  const userInfo = keycloak.tokenParsed;
  const isProUser = keycloak.hasRealmRole('pro_user');

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const logout = () => {
    keycloak.logout();
  };

  return (
    <div>
      <IconButton
        edge="end"
        color="inherit"
        onClick={handleMenu}
        aria-label="account of current user"
        aria-controls="profile-menu"
        aria-haspopup="true"
        sx={{ ml: 2 }}
      >
        <Avatar>
          <AccountCircleIcon />
        </Avatar>
      </IconButton>
      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem disabled>
          <Typography variant="subtitle1">
            {userInfo?.name || userInfo?.preferred_username}
          </Typography>
        </MenuItem>
        <MenuItem disabled>
          <Typography variant="body2">{userInfo?.email}</Typography>
        </MenuItem>
        <MenuItem disabled>
          <Typography variant="body2">
            Status: {isProUser ? 'Pro User' : 'Standard User'}
          </Typography>
        </MenuItem>
        <Divider />
        <MenuItem onClick={logout}>
          <Typography variant="body2">Logout</Typography>
        </MenuItem>
      </Menu>
    </div>
  );
}

export default ProfileMenu;
