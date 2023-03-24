/*
  Warnings:

  - You are about to drop the column `is_admin` on the `User` table. All the data in the column will be lost.

*/
-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('STUDENT', 'HEAD', 'ADMIN');

-- CreateEnum
CREATE TYPE "Team" AS ENUM ('FRONT_END', 'BACK_END', 'GRAPHIC', 'CLIENT', 'BRANDIND', 'EXECUTIVE', 'KERNEL', 'HR', 'DEVOPS', 'QA');

-- AlterTable
ALTER TABLE "User" DROP COLUMN "is_admin",
ADD COLUMN     "role" "UserRole" NOT NULL DEFAULT 'STUDENT',
ADD COLUMN     "team" "Team" NOT NULL DEFAULT 'FRONT_END';
