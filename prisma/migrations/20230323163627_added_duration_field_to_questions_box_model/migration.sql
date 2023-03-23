/*
  Warnings:

  - Added the required column `duration` to the `QuestionsBox` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "QuestionsBox" ADD COLUMN     "duration" INTEGER NOT NULL;
