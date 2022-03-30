#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>


size_t dummy(char* dir_name);

int main(int argc, char** argv) { 
/*
   int result;
   result = mkdir("ProcessedGames/testdir", 0777);
   printf("Return value was %d\n", result);
*/
/*
   char* DESTINATION_DIR = "ProcessedGames/";
   char* dirn = "trick room";

   size_t battle_num = 1;

   char* dest_path = malloc(strlen(DESTINATION_DIR) + strlen(dirn) + 1 + strlen("Battle") + 6 + 1);
   strcpy(dest_path, DESTINATION_DIR);
   strcpy(dest_path + strlen(DESTINATION_DIR), dirn);
   strcpy(dest_path + strlen(DESTINATION_DIR) + strlen(dirn), "/");
   strcpy(dest_path + strlen(DESTINATION_DIR) + strlen(dirn) + 1, "Battle");

   char* number = malloc(7);
   snprintf(number, 7, "%06zu", battle_num);
   number[6] = '\0';
 
   strcpy(dest_path + strlen(DESTINATION_DIR) + strlen(dirn) + 1 + strlen("Battle"), number); 

   printf("%s\n", number);
   printf("%s\n", dest_path);

   free(number); free(dest_path);
*/
   if(argc != 2) { printf("Add a directory\n"); return 1; }

   struct dirent* dirent;
   DIR* dir = opendir(argv[1]);

   if(!dir) {
      printf("Couldnt open directory");
      return 1;
   }

   while( (dirent = readdir(dir)) ) {
      if(strcmp(dirent->d_name, ".") && strcmp(dirent->d_name, "..")) {
         printf("%s\n", dirent->d_name);
      }
   }

   closedir(dir);

   printf("Found %lu files in the dirc\n", dummy("TBAnalyzed/trick room"));
 
   return 0;
}

size_t dummy(char* dir_name) {
   struct dirent* dirn;
   DIR* dirc = opendir(dir_name);

   if (!dirc) {
      return -1;
   }

   size_t num = 0;
   while( (dirn = readdir(dirc)) ) { num++; }

   closedir(dirc);
   return num; 
}
