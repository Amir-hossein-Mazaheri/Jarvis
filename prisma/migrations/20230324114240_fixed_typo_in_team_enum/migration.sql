/*
  Warnings:

  - The values [BRANDIND] on the enum `Team` will be removed. If these variants are still used in the database, this will fail.

*/
-- AlterEnum
BEGIN;
CREATE TYPE "Team_new" AS ENUM ('FRONT_END', 'BACK_END', 'GRAPHIC', 'CLIENT', 'BRANDING', 'EXECUTIVE', 'KERNEL', 'HR', 'DEVOPS', 'QA', 'NO_TEAM');
ALTER TABLE "User" ALTER COLUMN "team" DROP DEFAULT;
ALTER TABLE "User" ALTER COLUMN "team" TYPE "Team_new" USING ("team"::text::"Team_new");
ALTER TABLE "QuestionsBox" ALTER COLUMN "team" TYPE "Team_new" USING ("team"::text::"Team_new");
ALTER TYPE "Team" RENAME TO "Team_old";
ALTER TYPE "Team_new" RENAME TO "Team";
DROP TYPE "Team_old";
ALTER TABLE "User" ALTER COLUMN "team" SET DEFAULT 'NO_TEAM';
COMMIT;
