import React, { useRef, useState } from "react";
import { Button } from "@mui/material";
import { shallow } from "zustand/shallow";

import useUsersStore from "../store/useUsersStore";
import useTasksStore from "../store/useTasksStore";

const Publish = () => {
  const [error, setError] = useState("");

  const downloadBtnRef = useRef<HTMLAnchorElement>(null);

  const { users, clearUsers } = useUsersStore((store) => store, shallow);
  const { all, tasks, clearTasks } = useTasksStore((store) => store, shallow);

  const handlePublish = () => {
    if (all === "specified") {
      if (!users.length) return setError("کاربران نمیتونه خالی باشه");

      for (const user of users) {
        if (!user.tasks.length)
          return setError(
            "همه کاربرانی که اضافه کرده اید، حداقل یک تسک باید داشته باشد"
          );
      }
    } else {
      if (!tasks.length) return setError("حداقل یک تسک باید اضافه کنید");
    }

    setError("");

    if (downloadBtnRef.current) {
      const taskBlob = new Blob(
        [
          JSON.stringify(
            all === "all"
              ? { tasks }
              : users.map(({ username, tasks }) => ({ username, tasks }))
          ),
        ],
        { type: "application/json" }
      );

      downloadBtnRef.current.href = URL.createObjectURL(taskBlob);
      downloadBtnRef.current.download = "tasks.json";

      downloadBtnRef.current.click();

      URL.revokeObjectURL(downloadBtnRef.current.href);
    }

    all === "all" ? clearTasks() : clearUsers();
  };

  return (
    <div className="mt-8 mb-12">
      <div className="hidden">
        <a ref={downloadBtnRef}></a>
      </div>

      <div>
        <Button
          fullWidth
          variant="contained"
          color="info"
          size="large"
          onClick={handlePublish}
        >
          آماده سازی
        </Button>
      </div>
      {!!error && <div className="font-bold text-red-500 mt-5">{error}</div>}
    </div>
  );
};

export default Publish;
