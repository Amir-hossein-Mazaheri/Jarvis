/*
  Warnings:

  - Added the required column `team` to the `QuestionsBox` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "QuestionsBox" ADD COLUMN     "team" "Team" NOT NULL;
