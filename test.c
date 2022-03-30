#include "pokemon.h"
#include "team.h"

void testPokemon();
void testTeam();

int main(int argc, char** argv) {
   testTeam();   

   return 0;
}


void testPokemon(void) {
   char* moves[4] = {"Bubble Beam", "Withdraw", "Rapid Spin", NULL};
 
   pokemon* squirtle = Pokemon("Squirtle", NULL, moves, NULL);

   printMonInfo(squirtle);

   printf("%d\n", addMove(squirtle, "Protect"));

   printMonInfo(squirtle);

   printf("%d\n", addMove(squirtle, "Hyper Beam"));
   
   printMonInfo(squirtle);
 
   printf("%d\n", addAbility(squirtle, "Torrent"));

   printMonInfo(squirtle);

   printf("%d\n", addAbility(squirtle, "Libero"));

   printMonInfo(squirtle);

   printf("%d\n", addItem(squirtle, "Leftovers"));

   printMonInfo(squirtle);

   printf("%d\n", addItem(squirtle, "Life Orb"));

   printMonInfo(squirtle);

   releasePokemon(squirtle);

   return;

}

void testTeam(void) {
   team* squad = Team();

   printTeamInfo(squad);


   printf("%d\n", addPokemon(squad, "Squirtle", NULL, NULL, NULL));

   printTeamInfo(squad);


   printf("%d\n", addPokemon(squad, "Bulbasaur", NULL, NULL, NULL));
   printf("%d\n", addPokemon(squad, "Charmander", NULL, NULL, NULL));
   printf("%d\n", addPokemon(squad, "Pikachu", NULL, NULL, NULL));
   printf("%d\n", addPokemon(squad, "Caterpie", NULL, NULL, NULL));
   printf("%d\n", addPokemon(squad, "Weedle", NULL, NULL, NULL));
   printf("%d\n", addPokemon(squad, "Mewtwo", NULL, NULL, NULL));

   printTeamInfo(squad);


   printf("%d\n", updateStatus(squad, "Charmander", 1));
   printf("%d\n", updateStatus(squad, "Weedle", 2));
 
   printTeamInfo(squad);

   
   printf("%d\n", updateMoveset(squad, "Bulbasaur", "Vine Whip"));
   printf("%d\n", updateMoveset(squad, "Bulbasaur", "Tackle"));
   printf("%d\n", updateMoveset(squad, "Bulbasaur", "Giga Drain"));
   printf("%d\n", updateMoveset(squad, "Bulbasaur", "Leech Seed"));
   printf("%d\n", updateMoveset(squad, "Bulbasaur", "Mega Blast Move"));

   printTeamInfo(squad);

   
   printf("%d\n", updateItem(squad, "Weedle", "Life Orb"));

   printTeamInfo(squad);


   printf("%d\n", updateAbility(squad, "Bulbasaur", "Overgrowth"));

   printTeamInfo(squad);


   disbandTeam(squad);
}


