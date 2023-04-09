import React, { useEffect } from "react";

import AddUserBar from "./components/AddUserBar";
import Users from "./components/Users";
import Publish from "./components/Publish";
import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
} from "@mui/material";
import useTasksStore, { TaskType } from "./store/useTasksStore";
import { shallow } from "zustand/shallow";
import Tasks from "./components/Tasks";

// @ts-ignore
export const telegram = window.Telegram.WebApp;

console.log("\n\ntelegram: \n", telegram, "\n\n");

const App = () => {
  const { all, setAll } = useTasksStore((store) => store, shallow);

  useEffect(() => {
    telegram.ready();
    telegram.BackButton.show();
  }, []);

  return (
    <div className="px-24 py-16 w-full min-h-screen">
      <FormControl sx={{ my: "1.25rem" }}>
        <FormLabel id="select-task-type">نوع تسک</FormLabel>
        <RadioGroup
          row
          value={all}
          onChange={(e) => setAll(e.target.value as TaskType)}
          aria-labelledby="select-task-type"
          name="select-task-type"
        >
          <FormControlLabel
            value="specified"
            control={<Radio />}
            label="تسک جزئی"
          />
          <FormControlLabel value="all" control={<Radio />} label="تسک کلی" />
        </RadioGroup>
      </FormControl>

      {all === "specified" && <AddUserBar />}
      <Publish />
      {all === "all" ? <Tasks /> : <Users />}
    </div>
  );
};

export default App;
