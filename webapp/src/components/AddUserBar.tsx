import React, { useState } from "react";
import useSWR from "swr";
import {
  Button,
  InputLabel,
  MenuItem,
  Select,
  FormControl,
} from "@mui/material";
import { shallow } from "zustand/shallow";

import useUsersStore from "../store/useUsersStore";
import { getUsers } from "../utils/get-users";

const AddUserBar = () => {
  const [selectedUser, setSelectedUser] = useState("");

  const { data, error, isLoading } = useSWR("/team-users", getUsers);

  const { addUser } = useUsersStore((store) => store, shallow);

  const handleAddUser = () => {
    const [username, nickname] = JSON.parse(selectedUser);
    addUser(username, nickname);
    setSelectedUser("");
  };

  if (error) {
    return <p>{JSON.stringify(error)}</p>;
  }

  if (!data) {
    return <p>لودینگ...</p>;
  }

  return (
    <div className="px-6 py-4 mb-12 shadow">
      <h2 className="text-2xl font-bold mb-6">افزودن کاربر</h2>

      <div className="flex md:flex-row flex-col items-center gap-8">
        <FormControl fullWidth className="basis-4/5" variant="standard">
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
            {data.map(({ id, username, nickname }) => (
              <MenuItem key={id} value={JSON.stringify([username, nickname])}>
                {nickname}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          fullWidth
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
