import React, { useState } from "react";
import {
  Button,
  InputLabel,
  MenuItem,
  Select,
  FormControl,
} from "@mui/material";
import { shallow } from "zustand/shallow";

import useUsersStore from "../store/useUsersStore";

const AddUserBar = () => {
  const [serverUsers, setServerUsers] = useState([
    {
      username: "GGBoy313",
      name: "Amirhossein Mazaheri",
      studentCode: "40016763",
    },
    {
      username: "Akbari12",
      name: "Akbari",
      studentCode: "40016763",
    },
    {
      username: "ZerOne",
      name: "Jesus Christ",
      studentCode: "40016763",
    },
    {
      username: "YasinD",
      name: "Yasin",
      studentCode: "40016763",
    },
  ]);
  const [selectedUser, setSelectedUser] = useState("");

  const { addUser } = useUsersStore((store) => store, shallow);

  const handleAddUser = () => {
    addUser(selectedUser);
    setSelectedUser("");
    setServerUsers((users) => users.filter((u) => u.username !== selectedUser));
  };

  return (
    <div className="px-6 py-4 mb-12 shadow">
      <h2 className="text-2xl font-bold mb-6">افزودن کاربر</h2>

      <div className="flex items-center gap-8">
        <FormControl
          className="basis-4/5"
          variant="standard"
          sx={{ m: 1, minWidth: 120 }}
        >
          <InputLabel id="demo-simple-select-filled-label">
            انتخاب کاربر
          </InputLabel>
          <Select
            fullWidth
            labelId="demo-simple-select-filled-label"
            id="demo-simple-select-filled"
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
          >
            {serverUsers.map(({ username, name, studentCode }) => (
              <MenuItem key={username} value={username}>
                {name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="contained"
          size="large"
          onClick={handleAddUser}
          className="basis-1/5"
        >
          افزودن کاربر
        </Button>
      </div>
    </div>
  );
};

export default AddUserBar;
