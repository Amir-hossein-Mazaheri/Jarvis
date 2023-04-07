import React, { useEffect } from "react";

import User from "./components/User";
import AddUserBar from "./components/AddUserBar";
import Users from "./components/Users";
import Publish from "./components/Publish";

// @ts-ignore
export const telegram = window.Telegram.WebApp;

console.log("\n\ntelegram: \n", telegram, "\n\n");

const App = () => {
  useEffect(() => {
    telegram.ready();
    telegram.BackButton.show();
  }, []);

  return (
    <div className="px-24 py-16 w-full min-h-screen">
      <AddUserBar />
      <Publish />
      <Users />
    </div>
  );
};

export default App;
