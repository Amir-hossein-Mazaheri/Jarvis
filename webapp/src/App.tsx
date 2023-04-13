import React, { useEffect } from "react";
import {
  FormControl,
  FormControlLabel,
  FormLabel,
  Radio,
  RadioGroup,
} from "@mui/material";
import { shallow } from "zustand/shallow";
import { useAutoAnimate } from "@formkit/auto-animate/react";

import Publish from "./components/Publish";
import AddUserBar from "./components/AddUserBar";
import Users from "./components/Users";
import useTasksStore, { TaskType } from "./store/useTasksStore";
import Tasks from "./components/Tasks";

const App = () => {
  const { all, setAll } = useTasksStore((store) => store, shallow);

  const [container] = useAutoAnimate<HTMLDivElement>();

  return (
    <div
      ref={container}
      className="lg:px-24 lg:py-16 px-6 py-6 w-full min-h-screen"
    >
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
