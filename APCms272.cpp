/*
Version: 2015/12/14
Update:
1. In previous version, we kept positions for unhappy hosts for identification
But this time we use id insted of position
2. every host position will be used as MAP. activation is done sequentially using greedy method
a) find an unhappy AP
b) sort associated hosts using link speed
c) remove a host sequentially and activate it as MAP
d) check the average throughput constraint.
e) repeat the whole procedure until AP becomes Happy
*/
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>
#define DEFAULT_MAX_AP 100         //Deafult Maximum AP
#define DEFAULT_MAX_HOST 100       //Default Mahimum Host per AP
#define DEFAULT_MAX_GROUP 6       //Deafult Maximum AP
#define MAX_NO_OF_WALLS 20        //Default Maximum # of Walls in the network field

#define MAX_TYPE_WALLS 7

#define LINK_SPEED_DROP_PER_WALL 15 // Percentage of link speed drop per wall

#define INITIAL_MAX_TX_TIME 1000.0 //Initial Maximum TxTime for hill climbing
#define LOOP_COUNT_LB_HOST_COUNT 10000  //Default # of iteration for load balancing using #of host/AP
#define LOOP_COUNT_LB_LINK_SPEED 100  //Default # of iteration for swapping for Association optimization

#define RAND_SEED 50

    void inputNetworkInfo(const char *);
    void inputUnhappyHost(const char *);
    void calculateNoOfWallsBtwEachHost_AP_Pair();
    void adjustNodeCoordsUsingGridScale();
    void determineAssociabilityOfAP_HostUsingLinkSpeedThreshold();
    void determineAssociabilityOfAP_HostUsingOnlyCoverageRadius();
    void makeAcopy(struct APInfo *FromAIInfo, struct APInfo *ToAIInfo);
    void PHASE_ASSOCIATION_MODIFICATION();
    float calTx4APINC(int AP_index);
    void PHASE_BALANCING_NO_OF_HOSTS();
    void PHASE_RANDOM_SWAP_FOR_LINK_SPEED_UPDATE();
    void PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();
    void TEST_NEAREST_AP_HOST_ASSOCIATION();
    void phase_initialization();
    void phase_initial_solution_search();
    void phase_AP_host_association_optimization();
    void phase_additional_AP_activation();
    void PHASE_AP_SELECTION_OPTIMIZATION_ADJUSTED();
    void Hill_Climbing_Stage_in_AP_SELECTION_OPTIMIZATION();

    void generateOutputAndSimulationInputFiles(const char *, struct APInfo *localAIActive, struct HostInfo *localHIActive );

    float Local_Sesrch_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();

    void PostAssociationOptimization();

    char* substring(const char* str, size_t begin, size_t len);
    float distance(float x_1,float y_1,float x_2,float y_2);

    void SaveSolution(struct APInfo *FromAIInfo, struct APInfo *ToAIInfo, struct HostInfo *FromHIInfo, struct HostInfo *ToHIInfo);

    float calculateMaxTxTimeAmongAPs();
    void calculateTotalSpeedAmongAPs();
    float calculateTxTimeForAP(int AP_index);
    void generateListOfMovableHostsForMaxTxTimeAP();
    void calculateInitialAP_HostLinkSpeed();
    float LinkSpeedEstimationFunction(float distanceBtwAP_Host);

    float calculateLinkSpeedCostFunction();
    float calculateSumLinkSpeedForAP(int AP_index);
    float calculateSumOfAllLinkSpeed();
    int ifCurrentlySwappable(int HostA, int HostB);

    void inputChannelIDforActiveAPs();


    void read_wallInfo();
    double pathLossModel(int i, int j);
    double trans_speed(double distance);
    double pathLossModel5g(int i, int j);
    double trans_speed5g(double distance);
    void displayactiveassociation();
    void generatefileforpower();
    void generateFileCA(const char *phaseName, struct APInfo *localAIActive, struct HostInfo *localHIActive);


    static int IsOnSegment(double xi, double yi, double xj, double yj,
                        double xk, double yk);
    static char ComputeDirection(double xi, double yi, double xj, double yj,
                             double xk, double yk);
    /** Do line segments (x1, y1)--(x2, y2) and (x3, y3)--(x4, y4) intersect? */
    int DoLineSegmentsIntersect(double x1, double y1, double x2, double y2,
                             double x3, double y3, double x4, double y4);

    void printOutput(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void prepareInputFileForSimulatorInputGenerator(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void prepareInputFileForPerlProgramToDrawAssociation(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);

    void generateFIELD_File(char *);
    void generateNIC_File(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void generateNODE_File(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void generateNODE_File1(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void generateROUTE_File(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void generateSAP_File(char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);

    void generateFinalOPF(const char *, struct APInfo *localAIActive, struct HostInfo *localHIActive);
    void generateAdjustmentSpeed(const char *, int ifAdj, float T_BW, float T_S);
    void sortHostinAP(int indx);

    int gridSizeX,gridSizeY;
    int gridScale;
    float APCoverageRm; // coverage radius of APs in meters
    int needToadjust = 0;
    int NoAPAll;
    int NoAPReal;
    int NoAP; // No. of APs
    int NoHost; // No. of Hosts
    int NoGroup;
    int Aggr[DEFAULT_MAX_GROUP][DEFAULT_MAX_GROUP]; // Aggr[i][j]=0 -> can't aggregate, 1 -> Can Aggregate
    int NoChanel;
    int MaxHost; // Max Host per AP
    float linkSpeedThreshold;       // Link speed threshold in MbPs (new)
    float AverageHostThroughputThreshold; //the minimum average throughput of a host while the full network is operating.

    struct APInfo                                           // Start from 0 - used as array index
    {
        int APID;
        float PositionX,PositionY;
        int GroupID;
        int NoConHost;
        int ConHost[DEFAULT_MAX_HOST];  // list of connected hosts  // Value start from 1 - used for actual order of host on field, start from 1

        int ifActive;   // 0 -> inactive, 1-> active
        int HostMargin; // How many more host can be associated (limited to max#of host/AP permitted: MaxHost)
        int ifSatisfied; // 0 -> not satisfied, 1 -> satisfied
        int type; //0-> dedicated AP // 2-> virtual AP //2->mobile AP
        int participateInSelection; //0->yes// 1-> no
        int nodeID;
        int ChannelID;
    } AI[DEFAULT_MAX_AP],AINew[DEFAULT_MAX_AP],AIActive[DEFAULT_MAX_AP],AITempSol[DEFAULT_MAX_AP],AIBestSol[DEFAULT_MAX_AP], AIOldBestSol[DEFAULT_MAX_AP],AIActive4INC[DEFAULT_MAX_AP];

    struct HostInfo                                     // Start from 0 - used as array index
    {
        int HostID;
        float PositionX,PositionY;
        int GroupID;
        float HostActiveRate;
        int NoConAP;
        int ConAP[DEFAULT_MAX_AP];
        float AP_HostLinkSpeed[DEFAULT_MAX_AP];
         float AP_HostLinkSpeed2g[DEFAULT_MAX_AP];
          float AP_HostLinkSpeed5g[DEFAULT_MAX_AP];
        int AssocAP; // Actually associated AP
        float AssocAP_HostLinkSpeed;    // link speed to the associated AP
        int NoSat;  // #of associable active APs which are satisfied
        int SatAP[DEFAULT_MAX_AP]; // List associable active APs which are satisfied
        int nodeID;
        int ChannelID;
        int movable;
    } HI[DEFAULT_MAX_HOST],HINew[DEFAULT_MAX_HOST],HIActive[DEFAULT_MAX_HOST],HITempSol[DEFAULT_MAX_HOST],HIBestSol[DEFAULT_MAX_HOST], HIOldBestSol[DEFAULT_MAX_HOST];
         //for estimation model
     int NoOfWalls;
    struct WallInfo
    {
        float start_x;
        float start_y;
        float end_x;
        float end_y;
        int type;
        int numofwall;
    }Walls[MAX_TYPE_WALLS][MAX_NO_OF_WALLS];

    int NoOfWallsBtwHostAPPair[100][100][MAX_TYPE_WALLS]; // # of walls between each host-AP pair
    int wtype[MAX_TYPE_WALLS], NoTypeWalls;
    int NoOfWallsEachType[MAX_NO_OF_WALLS];





    int LOOP_COUNT_LB_TX_TIME;// S = 20000  // *********** Default # of iteration for load balancing using AP Tx Speed
    int LOOP_COUNT_HILL_CLIMB_LB_TX_TIME; // R = 75  // ************* Default # of iteration for continuing local search on load balancing using AP Tx Speed to reach global minima
    int LOOP_COUNT_AP_SELECTION_OPTIMIZATION; // U = 15 // ***********

    int HILL_CLIMB_MUTATION_FACTOR;   // Q // % of hosts whose association shall be changed by hill climbing method
    int AP_SELECTION_HILL_CLIMBING_RATIO; // T // Percentage of Active APs to be deactivated in Hill-climbing section in AP Selection Optimization stage

    float THROUGHPUT_IMPROVE_MARGIN;
    float AP_HostLinkSpeed[DEFAULT_MAX_AP][DEFAULT_MAX_HOST];
    float AP_HostLinkSpeed2g[DEFAULT_MAX_AP][DEFAULT_MAX_HOST];
    float AP_HostLinkSpeed5g[DEFAULT_MAX_AP][DEFAULT_MAX_HOST];

    int E_HostCount, newE_HostCount, delE_HostCount;
    float E_linkSpeed, newE_linkSpeed, delE_linkSpeed;

    int failureFlag=0; // Used for swapping AP association betweem two Hosts

    int flag;
    int vap_1st=0;

    int GlobalMaxTxTimeAP;//, GlobalBestNoOfAPs;


    const char *s1, *ipFileNamePart;
    char opFileName[80],opFileType[4];
    char FIELD_infoFileName[80],FIELD_infoFileType[4];
    char NIC_infoFileName[80], NIC_infoFileType[4];
    char NODE_infoFileName[80],NODE_infoFileType[4];
    char ROUTE_infoFileName[80],ROUTE_infoFileType[4];
    char SAP_patternFileName[80],SAP_patternFileType[4];

    char ipChannelIDFileName[80];
    char SimulatorInputGeneratorFileName[80],SimIPGenInputFileType[4];
    char DrawAssociationInputFileName[80],DrawAssociationInputFileType[4];

    float fnlThroughput;

    int numVAP, numMobAP,numDefectAP, mobileAP =0;;
    float adjustedRatio = 1.0, totalBandwidth;
    float speedOfAPs, speedOfMAP, speedOfVAP, speedOfRAP;


int vAPused = 0;
int mAPused = 0;

int main(int argc, char *argv[])
{

    int noOfActiveAp, sumLinkCandidate;
    float tempSumAP_HostLinkSpeed;

    srand ( atoi(argv[4]) );

    // Preparing input file name part
    s1=(const char *) argv[1];
    ipFileNamePart = substring(s1, 5, strlen(s1)-5-4);

    inputNetworkInfo(argv[1]);
    read_wallInfo();

    NoAPAll = 0;
    NoAPReal = 0;
    numMobAP = 0;
    numVAP = 0;
    numDefectAP = 0;
    for (int i = 0; i < NoAP; i++)
        {
        if(AI[i].type == 0)
            {
            NoAPAll++;
            NoAPReal++;
            AI[i].participateInSelection = 1;
            }
        else if(AI[i].type == 1)
            {
            numVAP++;
            AI[i].participateInSelection = 0;
            }
        else if(AI[i].type == 2)
            {
            numMobAP++;
            AI[i].participateInSelection = 0;
            }
        else
            {
            numDefectAP++;
            AI[i].participateInSelection = 0;
            }
    }

    LOOP_COUNT_LB_TX_TIME = atoi(argv[5]); // S
    LOOP_COUNT_HILL_CLIMB_LB_TX_TIME = atoi(argv[6]); // R
    LOOP_COUNT_AP_SELECTION_OPTIMIZATION = atoi(argv[7]); //U

    HILL_CLIMB_MUTATION_FACTOR = atoi(argv[8]);   // Q  = 10% of movable hosts
    AP_SELECTION_HILL_CLIMBING_RATIO = atoi(argv[9]); // T

    THROUGHPUT_IMPROVE_MARGIN = strtod(argv[10], NULL);

    linkSpeedThreshold = strtod(argv[2], NULL);

    AverageHostThroughputThreshold = strtod(argv[3], NULL);
    totalBandwidth = atof(argv[11]);
    calculateNoOfWallsBtwEachHost_AP_Pair();

    determineAssociabilityOfAP_HostUsingOnlyCoverageRadius();


    phase_initialization();

    sumLinkCandidate = 0;
    for(int i = 0; i < NoAP; i++)
    {
        tempSumAP_HostLinkSpeed=0.0;
        if(AINew[i].participateInSelection == 0)
            continue;
        sumLinkCandidate = sumLinkCandidate + AINew[i].NoConHost;
        for(int j = 0; j < AINew[i].NoConHost; j++)
        {
            tempSumAP_HostLinkSpeed = tempSumAP_HostLinkSpeed + AP_HostLinkSpeed[i][AINew[i].ConHost[j]-1];
        }
    }

    phase_initial_solution_search();

    noOfActiveAp=0;
    for(int i=0; i<NoAP; i++)
        {
        if(AIActive[i].participateInSelection == 0)
            continue;
            if(AIActive[i].NoConHost == 0)
                continue;
             if(AIActive[i].ifActive == 1)
             {
                 AIActive[i].nodeID = noOfActiveAp;
                 noOfActiveAp++;
             }
        }

    for (int i=0; i<NoHost; i++)
    {
        HIActive[i].HostID = HINew[i].HostID;
        HIActive[i].PositionX = HINew[i].PositionX;
        HIActive[i].PositionY = HINew[i].PositionY;
        HIActive[i].GroupID = HINew[i].GroupID;
        HIActive[i].HostActiveRate = HINew[i].HostActiveRate;
        HIActive[i].AssocAP = HINew[i].AssocAP;
        HIActive[i].movable = HINew[i].movable;
        HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP-1][i];

        HIActive[i].nodeID = noOfActiveAp+i;

        HIActive[i].NoConAP = 0;
        for (int j=0; j<HINew[i].NoConAP; j++)
        {
            if(AIActive[HINew[i].ConAP[j]-1].ifActive==1)  // consider only Active APs as associable APs
            {
                HIActive[i].ConAP[HIActive[i].NoConAP] = HINew[i].ConAP[j];
                HIActive[i].AP_HostLinkSpeed[HIActive[i].NoConAP] = AP_HostLinkSpeed[HINew[i].ConAP[j]-1][i];
                HIActive[i].NoConAP++;
            }
        }

    }

    phase_AP_host_association_optimization();
    phase_additional_AP_activation();
     //displayactiveassociation();



    //calculateTotalSpeedAmongAPs();


    /*int ch =1;
    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].NoConHost == 0)
                continue;
    if(AIActive[i].ifActive == 1)
    {
        AIActive[i].ChannelID = ch;
        ch++;
    }

    }

    noOfActiveAp=0;
    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].NoConHost == 0)
        {
        AIActive[i].ifActive = 0;
        continue;
        }
    if(AIActive[i].ifActive == 1)
    {
        AIActive[i].nodeID = noOfActiveAp;
        noOfActiveAp++;
    }
    }
    for (int i=0; i<NoHost; i++)    HIActive[i].nodeID = noOfActiveAp+i;

    float fnlMaxTx = calculateMaxTxTimeAmongAPs();
    fnlThroughput = 1/fnlMaxTx;
    printf("\n final..%f", fnlThroughput);
*/

    //displayactiveassociation();
   // printf("------------------------------------\n");
// edit start 19/08/21
    for(int i=0; i<NoAP; i++)
    {
        if(AIActive[i].ifActive==1 && i%2==0)
        {
            if(AIActive[i+1].ifActive==0)

            {
                AIActive[i+1].ifActive=1;
                for(int j=0;j<NoHost;j++)
                {
                    HIActive[j].ConAP[HIActive[j].NoConAP]=i+2;   // increase the associable AP list
                    HIActive[j].NoConAP++;
                }
            }

        }
    }
    /*for(int j=0;j<NoHost;j++)
    {
        //printf("Host %d\t AP=%d\n",j+1, HIActive[j].NoConAP);
        for(int i=0;i<HIActive[j].NoConAP;i++)
          //  printf("%d\t", HIActive[j].ConAP[i]);
        printf("\n");

    }*/
printf("After optimization\n");
   // PostAssociationOptimization();
  //TEST_NEAREST_AP_HOST_ASSOCIATION();
   PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();
   PostAssociationOptimization();
   calculateTotalSpeedAmongAPs();

     for(int i=0; i<NoAP; i++)
     {
         if (AIActive[i].ifActive==1)
            printf("\nList of Active AP=%d\n",i+1);

     }
     int ch =1;
    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].NoConHost == 0)
                continue;
    if(AIActive[i].ifActive == 1)
    {
        AIActive[i].ChannelID = ch;
        ch++;
    }

    }

    noOfActiveAp=0;
    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].NoConHost == 0)
        {
        AIActive[i].ifActive = 0;
        continue;
        }
    if(AIActive[i].ifActive == 1)
    {
        AIActive[i].nodeID = noOfActiveAp;
        noOfActiveAp++;
    }
    }
    for (int i=0; i<NoHost; i++)    HIActive[i].nodeID = noOfActiveAp+i;

    float fnlMaxTx = calculateMaxTxTimeAmongAPs();
    float fnlThroughput = 1/fnlMaxTx;
    printf("\n TTTTTTTTTTTTTfinal..%f\n", fnlThroughput);
     displayactiveassociation();
// edit end 19/08/21
    generateOutputAndSimulationInputFiles("AfterOptimization_", AIActive, HIActive);  // read this function
    generateFinalOPF("out.txt", AIActive, HIActive);
    generateAdjustmentSpeed("adjustment.txt", needToadjust, totalBandwidth, adjustedRatio);
    generateFileCA("ICA.txt", AIActive, HIActive);
    generatefileforpower();



    return 0;
}

void generateFileCA(const char *phaseName, struct APInfo *localAIActive, struct HostInfo *localHIActive){


    int noOfActiveAp, hostid;

    noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)
        {
        if(localAIActive[i].participateInSelection == 0)
            continue;
        if(localAIActive[i].NoConHost == 0)
            continue;
        if (localAIActive[i].ifActive == 1)
            {
                localAIActive[i].nodeID = noOfActiveAp;
                noOfActiveAp++;
            }

        }

    hostid=0;
    for (int i=0; i<NoHost; i++)
        {
        // if(activeHost[i]==1){
         localHIActive[i].nodeID = hostid; hostid++; //}
        //localHIActive[i].nodeID = noOfActiveAp+i;    // *** Assign Node ID for Hosts here
        }
    FILE *CAgen;

    CAgen = fopen(phaseName,"wt");
    fprintf(CAgen, "%d\n",noOfActiveAp);

    for(int i=0; i<NoAP; i++)
    {
    if(localAIActive[i].participateInSelection == 0)
            continue;
        if(localAIActive[i].ifActive == 1 && localAIActive[i].NoConHost != 0)
        {
            fprintf(CAgen, "%d\t%f\t%f\n",localAIActive[i].nodeID,localAIActive[i].PositionX, localAIActive[i].PositionY);
        }
    }

    //fprintf(CAgen, "\n");
    fprintf(CAgen, "%d\n",hostid);
    for(int j=0; j<NoHost; j++)
    {
       //if(activeHost[j]==1){
        fprintf(CAgen, "%d\t%f\t%f\t%d\n",localHIActive[j].nodeID,localHIActive[j].PositionX, localHIActive[j].PositionY, localAIActive[localHIActive[j].AssocAP-1].nodeID);
         //   }
    }

    fprintf(CAgen, "\n");
    //fprintf(CAgen, "%d",NoOfWalls);
    //for(int i=0; i<NoOfWalls; i++)
    //{
     //  fprintf(CAgen, "\n%f\t%f\t%f\t%f", Walls[i].start_x, Walls[i].start_y, Walls[i].end_x, Walls[i].end_y);
    //}
fclose(CAgen);

}

void generatefileforpower(){

    FILE *fp2;
    //int i,nap=0;
    int NAP=0;
    char filename[100]="association.txt";
    fp2 = fopen(filename,"w");
    for(int i=0; i<NoAP; i++)
    if(AIActive[i].ifActive == 1)
    NAP++;
    fprintf(fp2, "%d \n", NAP);
    for(int i=0; i<NoAP; i++) {
    if(AIActive[i].ifActive == 1){
    fprintf(fp2, "%d \t", i+1);
    fprintf(fp2, "%d \t", AIActive[i].NoConHost);
    for(int j=0; j<AIActive[i].NoConHost; j++)
          fprintf(fp2, "%d \t", AIActive[i].ConHost[j]);
            //printf("\n");
    fprintf(fp2, "\n");
    }
      //printf("\nAP- %d --:",i+1);

}
fclose(fp2);




    char filename1[100]="ICAspeed.txt";
    fp2 = fopen(filename1,"w");
    for(int i=0; i<NoAP; i++){
    if(AIActive[i].ifActive == 1)
    {
        for(int j=0;j<NoHost;j++)
        {
        fprintf(fp2, "%f \t", AP_HostLinkSpeed[i][j]);

        }
        fprintf(fp2, "\n");


    }
    }
   fclose(fp2);


   int noOfActiveAp, hostid;

    noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)
        {
        if(AIActive[i].participateInSelection == 0)
            continue;
        if(AIActive[i].NoConHost == 0)
            continue;
        if (AIActive[i].ifActive == 1)
            {
                AIActive[i].nodeID = noOfActiveAp;
                noOfActiveAp++;
            }

        }
    hostid=noOfActiveAp;
    for (int i=0; i<NoHost; i++)
    {
         //if(activeHost[i]==1){
         HIActive[i].nodeID = hostid; hostid++;// }
        //localHIActive[i].nodeID = noOfActiveAp+i;    // *** Assign Node ID for Hosts here
    }



    int initial_power=30;
    char filename2[100]="node_power.txt";
    fp2 = fopen(filename2,"w");


    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].participateInSelection == 0)
            continue;
        if(AIActive[i].ifActive == 1 && AIActive[i].NoConHost != 0)
        {
            fprintf(fp2, "%d\t%d\n",AIActive[i].nodeID,initial_power);
        }
    }



    for(int j=0; j<NoHost; j++)
    {
      // if(activeHost[j]==1){
        fprintf(fp2, "\n%d\t%d",HIActive[j].nodeID,initial_power);

    //}
    }

    fclose(fp2);





}


void displayactiveassociation()
{

for(int i=0; i<NoAP; i++) {
printf("\nAP- %d --:",i+1);
for(int j=0; j<AIActive[i].NoConHost; j++)
    printf("%d ", AIActive[i].ConHost[j]);
    printf("\n");
}

}

//Using Bubble Sort
void sortHostinAP(int indx)
{
        int AP_index =0;
        AP_index = indx;
        int tHostID;
        float tPositionX,tPositionY;
        int tGroupID;
        float tHostActiveRate;

        int tNoConAP;
        int tConAP[DEFAULT_MAX_AP]; // Connectible/Associable AP list  // Value start from 1 - used for actual order of AP on field, start from 1
        float tAP_HostLinkSpeed[DEFAULT_MAX_AP];// Signal strength from each associable AP     // 0 -> Weak, 1-> strong



        int tAssocAP; // Actually associated AP          // Start from 1 - used for actual order of AP on field, start from 1
        float tAssocAP_HostLinkSpeed;    // link speed to the associated AP

        int tNoSat;  // #of associable active APs which are satisfied
        int tSatAP[DEFAULT_MAX_AP]; // List associable active APs which are satisfied

        int tnodeID;
        int tChannelID;
        int tmovable;
        int tcon_host;
        struct APInfo t1APInfo;
        struct HostInfo thostInfo;


for( int c = 0; c <AIActive[AP_index].NoConHost;  c++)
{
    for( int d = 0; d <(AIActive[AP_index].NoConHost-1);  d++)
    {

    if(HIActive[AIActive[AP_index].ConHost[d]-1].AssocAP_HostLinkSpeed>HIActive[AIActive[AP_index].ConHost[d+1]-1].AssocAP_HostLinkSpeed)
        {
        tcon_host=AIActive[AP_index].ConHost[d];
        AIActive[AP_index].ConHost[d]= AIActive[AP_index].ConHost[d+1];
        AIActive[AP_index].ConHost[d+1]= tcon_host;
        }
    }
}

}

void inputUnhappyHost(const char *s2)
{
    FILE *ipfp;
    ipfp = fopen(s2,"rt");
    //ipfp = fopen("input3_3_Updated.txt","rt");

    fscanf(ipfp, "%d", &gridSizeX);
    fscanf(ipfp, "%d", &gridSizeY);
    fscanf(ipfp, "%d", &gridScale);



    fclose(ipfp);


}


void inputNetworkInfo(const char *s2)
{
    FILE *ipfp;
    ipfp = fopen(s2,"rt");
    fscanf(ipfp, "%d", &gridSizeX);
    fscanf(ipfp, "%d", &gridSizeY);
    fscanf(ipfp, "%d", &gridScale);

    fscanf(ipfp, "%f", &APCoverageRm);
    //fscanf(ipfp, "%f", &AdjApBW);

    fscanf(ipfp, "%d", &NoAP);
    fscanf(ipfp, "%d", &NoHost);
    fscanf(ipfp, "%d", &NoGroup);
    for (int i=0; i<NoGroup;i++) for (int j=0; j<NoGroup;j++)   fscanf(ipfp, "%d", &Aggr[i][j]);

    fscanf(ipfp, "%d", &NoChanel);
    fscanf(ipfp, "%d", &MaxHost);
    //fscanf(ipfp, "%f", &linkSpeedThreshold);

    for (int i=0;i<NoAP;i++)
    {
        fscanf(ipfp, "%d", &AI[i].APID);
        fscanf(ipfp, "%f", &AI[i].PositionX);
        //AI[i].PositionX += 5.0;
        fscanf(ipfp, "%f", &AI[i].PositionY);
        //AI[i].PositionY += 5.0;
        fscanf(ipfp, "%d", &AI[i].GroupID);

        fscanf(ipfp, "%d", &AI[i].type);
        //for (int j=0;j<AI[i].NoConHost;j++)     fscanf(ipfp, "%d", &AI[i].ConHost[j]);  // Critical: ----####----- Should be calculated from AP-HOST coordinates
    }
    //printf("%d ",AI[8].ConHost[AI[8].NoConHost-1]);
    for (int i=0;i<NoHost;i++)
    {
        fscanf(ipfp, "%d", &HI[i].HostID);
        fscanf(ipfp, "%f", &HI[i].PositionX);
        //HI[i].PositionX += 5.0;
        fscanf(ipfp, "%f", &HI[i].PositionY);
        //HI[i].PositionX += 5.0;
        fscanf(ipfp, "%d", &HI[i].GroupID);
        fscanf(ipfp, "%f", &HI[i].HostActiveRate);
        fscanf(ipfp, "%d", &HI[i].movable);
    }

    //fscanf(ipfp, "%d", &NoOfWalls);
    //for (int i=0;i<NoOfWalls;i++)  fscanf(ipfp, "%f %f %f %f", &Walls[i].start_x, &Walls[i].start_y, &Walls[i].end_x, &Walls[i].end_y);

    fclose(ipfp);
}

void read_wallInfo(){

    FILE *fp;
    int wn, i;
    if((fp = fopen("wall.txt","r")) == NULL){
		printf("wall file reading error 1:Can't open file \n");
		exit(1);
    }
    /*
    fscanf(fp, "%d", &wn);
    NoOfWalls = wn;
    for(i = 0; i<wn; i++)
        {
        fscanf(fp, "%f %f %f %f", &Walls[i].start_x, &Walls[i].start_y, &Walls[i].end_x, &Walls[i].end_y);
        }
       */

    fscanf(fp, "%d", &NoTypeWalls);

    for(int t = 0; t<NoTypeWalls; t++)
    {
    fscanf(fp, "%d  %d", &wtype[t], &NoOfWallsEachType[t]);

    for (int i=0;i<NoOfWallsEachType[t];i++)
      fscanf(fp, "%f %f %f %f", &Walls[t][i].start_x, &Walls[t][i].start_y, &Walls[t][i].end_x, &Walls[t][i].end_y);
      }
    fclose(fp);
    //fclose(fp);
/*
    printf("\n Total type of wall : %d", NoTypeWalls);
    for(int t = 0; t<NoTypeWalls; t++)
    {
    printf("\n type %d is : %d\n ", wtype[t], NoOfWallsEachType[t]);

    for (int i=0;i<NoOfWallsEachType[t];i++)
      printf("%.2f %.2f %.2f %.2f\n", Walls[t][i].start_x, Walls[t][i].start_y, Walls[t][i].end_x, Walls[t][i].end_y);
    printf("\n");

      }
      */



}


// ** Adjust the node (APs and Hosts) grid position by considering Grid scale. original position: = grid position * Grid scale/100
void adjustNodeCoordsUsingGridScale()
{
    for (int i=0;i<NoAP;i++)
    {
        AI[i].PositionX = AI[i].PositionX * gridScale / 100.0;
        AI[i].PositionY = AI[i].PositionY * gridScale / 100.0;
    }

    for (int i=0; i<NoHost; i++)
    {
        HI[i].PositionX = HI[i].PositionX * gridScale / 100.0;
        HI[i].PositionY = HI[i].PositionY * gridScale / 100.0;
    }
}


// ** Calculate # of walls between each AP-Host pair
void calculateNoOfWallsBtwEachHost_AP_Pair()
{
   // int i,j,k;
   // int NoOfIntersection;
/*
    for( i=0; i<NoHost; i++)
    {
        for( j=0; j<NoAP; j++)
        {
            NoOfIntersection = 0;
            for( k=0; k<NoOfWalls; k++)
            {
                if(DoLineSegmentsIntersect(HI[i].PositionX, HI[i].PositionY, AI[j].PositionX, AI[j].PositionY, Walls[k].start_x, Walls[k].start_y, Walls[k].end_x, Walls[k].end_y) == 1)  NoOfIntersection ++;

            }

            NoOfWallsBtwHostAPPair[i][j] = NoOfIntersection;

        }


    }

   */


   int i,j,k;
    int NoOfIntersection;
    /*
    for( i=0; i<NoHost; i++)
    {
        for( j=0; j<NoAP; j++)
        {
            NoOfIntersection = 0;
            for( k=0; k<NoOfWalls; k++)
            {
                if(DoLineSegmentsIntersect(HI[i].PositionX, HI[i].PositionY, AI[j].PositionX, AI[j].PositionY, Walls[k].start_x, Walls[k].start_y, Walls[k].end_x, Walls[k].end_y) == 1)  NoOfIntersection ++;

            }

            NoOfWallsBtwHostAPPair[i][j] = NoOfIntersection;

        }


    }

    */

    for( i=0; i<NoHost; i++)
    {
        for( j=0; j<NoAP; j++)
        {
           // NoOfIntersection = 0;
            for( int t=0; t<NoTypeWalls; t++){
            NoOfIntersection = 0;
            for( k=0; k<NoOfWallsEachType[t]; k++)
            {
                if(DoLineSegmentsIntersect(HI[i].PositionX, HI[i].PositionY, AI[j].PositionX, AI[j].PositionY, Walls[t][k].start_x, Walls[t][k].start_y, Walls[t][k].end_x, Walls[t][k].end_y) == 1)  NoOfIntersection ++;

            }

            NoOfWallsBtwHostAPPair[i][j][t] = NoOfIntersection;


            }

        }


    }

    //for(i= 0; i<N_NODE; i++){
    //for(j= 0; j<N_NODE; j++) {
      //  for( int t=0; t<NoTypeWalls; t++)
        //printf("\n HERE: %d %d %d ", i+1, j+1, NoOfWallsBtwHostAPPair[i][j][t]);
    //}
    //}

    FILE *fp;
    fp=fopen("intersection2.txt", "w");
    for(i= 0; i<NoHost; i++){
    fprintf(fp, "-------------------for %d (%.2f %.2f)-------------------------", i, HI[i].PositionX, HI[i].PositionY);
    for(j= 0; j<NoAP; j++) {
        fprintf(fp, "to %d :(%.2f %.2f)--->)", j,AI[j].PositionX, AI[j].PositionY);
        for( int t=0; t<NoTypeWalls; t++)
        fprintf(fp, "%d ", NoOfWallsBtwHostAPPair[i][j][t]);
        fprintf(fp, "\n");
    }
    }
    fclose(fp);
}

static int IsOnSegment(double xi, double yi, double xj, double yj,
                        double xk, double yk)
{
  return (xi <= xk || xj <= xk) && (xk <= xi || xk <= xj) &&
         (yi <= yk || yj <= yk) && (yk <= yi || yk <= yj);
}

static char ComputeDirection(double xi, double yi, double xj, double yj,
                             double xk, double yk)
{
  double a = (xk - xi) * (yj - yi);
  double b = (xj - xi) * (yk - yi);
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Do line segments (x1, y1)--(x2, y2) and (x3, y3)--(x4, y4) intersect? */
int DoLineSegmentsIntersect(double x1, double y1, double x2, double y2,
                             double x3, double y3, double x4, double y4) {
  char d1 = ComputeDirection(x3, y3, x4, y4, x1, y1);
  char d2 = ComputeDirection(x3, y3, x4, y4, x2, y2);
  char d3 = ComputeDirection(x1, y1, x2, y2, x3, y3);
  char d4 = ComputeDirection(x1, y1, x2, y2, x4, y4);
  return (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
          ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) ||
         (d1 == 0 && IsOnSegment(x3, y3, x4, y4, x1, y1)==1) ||
         (d2 == 0 && IsOnSegment(x3, y3, x4, y4, x2, y2)==1) ||
         (d3 == 0 && IsOnSegment(x1, y1, x2, y2, x3, y3)==1) ||
         (d4 == 0 && IsOnSegment(x1, y1, x2, y2, x4, y4)==1);
}


void determineAssociabilityOfAP_HostUsingOnlyCoverageRadius()
{
    // *** #### Critical : Have to check, if there exists hosts such that, it doesn't comes to associable hosts list of any AP
    float distanceBtwAP_Host;
    float tempLinkSpeed,tempLinkSpeed5g,tempLinkSpeed2g;

    for(int i=0; i<NoAP; i++) AI[i].NoConHost = 0;
    for(int j=0; j<NoHost; j++) HI[j].NoConAP = 0;

    // 2.4GHz Estimation
      for (int i=0;i<NoAP;i=i+2)
    {   //printf("TEST!!");
        for (int j=0; j<NoHost; j++)
        {
            distanceBtwAP_Host = distance( AI[i].PositionX, AI[i].PositionY, HI[j].PositionX, HI[j].PositionY );
            //tempLinkSpeed = calculateAP_HostLinkSpeed(distanceBtwAP_Host);
           // tempLinkSpeed = LinkSpeedEstimationFunction(distanceBtwAP_Host);
            double sigST2g = pathLossModel(i, j);
            //printf("sigST2g=%f\n",sigST2g);
            tempLinkSpeed2g = adjustedRatio * trans_speed(sigST2g);
            if(distanceBtwAP_Host <= APCoverageRm)
            {
                //printf("TEST!!");
                AI[i].ConHost[AI[i].NoConHost] = j+1;
                HI[j].ConAP[HI[j].NoConAP] = i+1;
                HI[j].AP_HostLinkSpeed[HI[j].NoConAP] = tempLinkSpeed2g;

                AI[i].NoConHost++;
                HI[j].NoConAP++;
            }
        }
    }
// 5GHz estimation
    for (int i=1;i<NoAP;i=i+2)
    {   //printf("TEST!!");
        for (int j=0; j<NoHost; j++)
        {
            distanceBtwAP_Host = distance( AI[i].PositionX, AI[i].PositionY, HI[j].PositionX, HI[j].PositionY );
            //tempLinkSpeed = calculateAP_HostLinkSpeed(distanceBtwAP_Host);
           // tempLinkSpeed = LinkSpeedEstimationFunction(distanceBtwAP_Host);
            double sigST5g = pathLossModel5g(i, j);
           // printf("sigST5g=%f\n",sigST5g);
            tempLinkSpeed5g = adjustedRatio * trans_speed5g(sigST5g);
            if(distanceBtwAP_Host <= APCoverageRm)
            {
                //printf("TEST!!");
                AI[i].ConHost[AI[i].NoConHost] = j+1;
                HI[j].ConAP[HI[j].NoConAP] = i+1;
                HI[j].AP_HostLinkSpeed[HI[j].NoConAP] = tempLinkSpeed5g;

                AI[i].NoConHost++;
                HI[j].NoConAP++;
            }
        }
    }
    //exit(1);


    //exit(1);
    /*for (int i=0;i<NoAP;i++)
    {
        for (int j=0; j<NoHost; j++)
        {
         printf("HI[j].AP_HostLinkSpeed[HI[j].NoConAP]=%f",HI[j].AP_HostLinkSpeed[HI[j].NoConAP]);
        }
    }*/



}

double pathLossModel(int i, int j)
{
double sigSt, distances;

double alpha=2.20;
double P1=-28.1;

double W[7]={0.0,7.5,6.0,4.0,2.5,2.4,2.0};
//double d_th=6.10;
//0 7 6 7 2.3 3.4 5.0

   distances = distance(AI[i].PositionX, AI[i].PositionY, HI[j].PositionX, HI[j].PositionY);

//calculate wall loss
    double totalloss=0.0;
    for( int t=0; t<NoTypeWalls; t++){
       totalloss=totalloss + NoOfWallsBtwHostAPPair[j][i][t]*W[t];

       }

    //printf("\ntotal loss of %d %d : %.2f",i+1,j+1, totalloss);
    //if(distances<=d_th)
    sigSt =  (double) (P1 - 10.0*alpha* log10(distances)-totalloss);
  //  else {
    //if((i==0 || i==2 ) && j==14)
    //printf("here my boy%f", distances);
   // sigSt =  (double) (P1 - 10.0*alpha1* log10(distances)-totalloss);
   // }


return sigSt;

}
double pathLossModel5g(int i, int j)
{
double sigSt, distances;

//double alpha=2.20;
double alpha=2.40;
double P1=-27.8;
//double P1=-40;
double W[7]={0.0,7.1,8.0,4.0,2.0,2.2,2.4};
//double d_th=6.10;
//0 7 6 7 2.3 3.4 5.0

   distances = distance(AI[i].PositionX, AI[i].PositionY, HI[j].PositionX, HI[j].PositionY);

//calculate wall loss
    double totalloss=0.0;
    for( int t=0; t<NoTypeWalls; t++){
       totalloss=totalloss + NoOfWallsBtwHostAPPair[j][i][t]*W[t];

       }

    //printf("\ntotal loss of %d %d : %.2f",i+1,j+1, totalloss);
   // if(distances<=d_th)
    sigSt =  (double) (P1 - 10.0*alpha* log10(distances)-totalloss);
    //else {
    //if((i==0 || i==2 ) && j==14)
    //printf("here my boy%f", distances);
//sigSt =  (double) (P1 - 10.0*alpha1* log10(distances)-totalloss);
   // }


return sigSt;

}

double trans_speed5g(double distance){
	double speed;

       // double a=64,b=56.5, c=6.5;
      // double a=64,b=47, c=5;
      double a=66,b=56.5, c=6.5;
//double a=44,b=45, c=5.30;
        speed = a / ( 1.0 + exp( -((distance+120) - b)/c));

	return speed;
}


double trans_speed(double distance){
	double speed;

        double a=33.75,b=57.0, c=6.5;
        speed = a / ( 1.0 + exp( -((distance+120) - b)/c));

	return speed;
}


void phase_initialization()
{
    int curHost,curAP;
    float maxLinkSpeedForHost[NoHost];
    int maxLinkSpeedAPforHost[NoHost];
    float tempLinkSpeed;
    calculateInitialAP_HostLinkSpeed();
    for (int i=0; i<NoHost; i++)
    {
        HINew[i].HostID = HI[i].HostID;
        HINew[i].PositionX = HI[i].PositionX;
        HINew[i].PositionY = HI[i].PositionY;
        HINew[i].GroupID = HI[i].GroupID;
        HINew[i].HostActiveRate = HI[i].HostActiveRate;
        HINew[i].movable = HI[i].movable;
        HINew[i].NoConAP = 0;

        maxLinkSpeedForHost[i] = 0.0;
        maxLinkSpeedAPforHost[i] = -1;
    }

    for (int i=0;i<NoAP;i++)
    {
        AINew[i].APID = AI[i].APID;
        AINew[i].PositionX = AI[i].PositionX;
        AINew[i].PositionY = AI[i].PositionY;
        AINew[i].GroupID = AI[i].GroupID;
        AINew[i].NoConHost = 0;
        AINew[i].participateInSelection = AI[i].participateInSelection;
        AINew[i].type = AI[i].type;

        for (int j=0;j<AI[i].NoConHost;j++)
        {
            if (Aggr[AI[i].GroupID-1][HI[AI[i].ConHost[j]-1].GroupID-1]==1)
            {
                tempLinkSpeed = AP_HostLinkSpeed[i][AI[i].ConHost[j]-1];
               //printf("tempLinkSpeed=%f\n",tempLinkSpeed);
                //printf("\nmaxLinkSpeedForHost[AI[%d].ConHost[%d]-1]=%f\n",i,j,maxLinkSpeedForHost[AI[i].ConHost[j]-1]);
                if(tempLinkSpeed > maxLinkSpeedForHost[AI[i].ConHost[j]-1])
                {
                    maxLinkSpeedForHost[AI[i].ConHost[j]-1] = tempLinkSpeed;
                    maxLinkSpeedAPforHost[AI[i].ConHost[j]-1] = i;
                }

                if(tempLinkSpeed >= linkSpeedThreshold)
                {
                    curAP=i+1;                  // Current AP and Host ID
                    curHost= AI[i].ConHost[j];
                    AINew[i].ConHost[AINew[i].NoConHost]= curHost;  // Connect current Host to current AP info
                    AINew[i].NoConHost++;
                    HINew[curHost-1].ConAP[HINew[curHost-1].NoConAP]=curAP;  // Connect current AP to current Host info
                    HINew[curHost-1].AP_HostLinkSpeed[HINew[curHost-1].NoConAP] = tempLinkSpeed;
                    HINew[curHost-1].NoConAP++; // NoConAP has already been initialized to zero. Now we are incrementing
                }
            }
        }

    }

    for (int i=0; i<NoHost; i++)
    {
        if(HINew[i].NoConAP == 0)
        {
          printf("BEST FIT!! ");

          curAP = maxLinkSpeedAPforHost[i];

          AINew[curAP].ConHost[AINew[curAP].NoConHost]= i+1;  // Connect current Host to current AP info
          AINew[curAP].NoConHost++;

          HINew[i].ConAP[HINew[i].NoConAP]=curAP+1;  // Connect current AP to current Host info
          HINew[i].AP_HostLinkSpeed[HINew[i].NoConAP]=maxLinkSpeedForHost[i];
          HINew[i].NoConAP++; //

        }
    }

    //1.(2): Initialize all physical APs to non-active APs
    for(int i=0; i<NoAP; i++)
    {
        AINew[i].ifActive = 0;
        AIActive[i].ifActive = 0;
        AIActive[i].type = AINew[i].type;
        AIActive[i].participateInSelection = AINew[i].participateInSelection;
        AIActive[i].APID = AINew[i].APID;
        AIActive[i].PositionX = AINew[i].PositionX;
        AIActive[i].PositionY = AINew[i].PositionY;
        AIActive[i].GroupID = AINew[i].GroupID;
        AIActive[i].NoConHost = 0;
    }
}

void phase_initial_solution_search()
{
    int max,maxAP;
    float maxSumAP_HostLinkSpeed,tempSumAP_HostLinkSpeed;

    for(int i=0;i<NoHost;i++)   HINew[i].AssocAP=-1; // initially no associated AP to any host // // Critical : link speed update here ----####----

    do
    {
        maxSumAP_HostLinkSpeed=0.0;
        maxAP=-1;
       //for(int i=0;i<NoAP;i++) // *** Among the non-active APs,Find the AP with the maximum no. of associable un-associated host
       for(int i=0;i<NoAP;i=i+2)
        {
            if(AINew[i].participateInSelection == 0)
            continue;
            if(AINew[i].ifActive == 0 ) // only non-actine AP
            {
                tempSumAP_HostLinkSpeed=0.0;
                for(int j=0;j<AINew[i].NoConHost;j++)
                {
                    if(HINew[AINew[i].ConHost[j]-1].AssocAP==-1)  tempSumAP_HostLinkSpeed = tempSumAP_HostLinkSpeed + AP_HostLinkSpeed[i][AINew[i].ConHost[j]-1];
                    }

                if(tempSumAP_HostLinkSpeed>maxSumAP_HostLinkSpeed)
                {
                    maxSumAP_HostLinkSpeed=tempSumAP_HostLinkSpeed;
                    maxAP=i;
                }
            }
        }

        if(maxAP!=-1)
        {
            AINew[maxAP].ifActive = 1;
            AIActive[maxAP].ifActive = 1;
            AIActive[maxAP].NoConHost = 0;

            for(int i=0;i<AINew[maxAP].NoConHost;i++) // Assocoate all associable un-associated hosts to maxAP
            {
                if(HINew[AINew[maxAP].ConHost[i]-1].AssocAP==-1)
                {
                    HINew[AINew[maxAP].ConHost[i]-1].AssocAP = maxAP+1;                             // Critical : link speed update here ----####----
                    HINew[AINew[maxAP].ConHost[i]-1].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[maxAP][AINew[maxAP].ConHost[i]-1];

                    AIActive[maxAP].ConHost[AIActive[maxAP].NoConHost]=AINew[maxAP].ConHost[i];

                    AIActive[maxAP].NoConHost++;    // NoConHost : It had been initialized to zero : now incrementing
                }
            }
        }

        flag=1;     // Check if any unallcated Host exists
        for(int i=0;i<NoHost;i++)
            if(HINew[i].AssocAP==-1)
            {
                flag=0;
                break;
            }

    }while(flag==0);
}

void PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP()
{
    int curHost,curAP;
    float tempMaxTxTime, globalMaxTxTime = INITIAL_MAX_TX_TIME; // Give a very big value to globalMaxTxTime
    int tempFlag, noOfMovableLowLSpHost, movableLowLSpHosts[NoHost];
    int noOfMovableHost, movableHost[NoHost], bestLSpAPforHost[NoHost]; // AP index start from 0
    float distanceBtwAP_Host, bestLSpforHost[NoHost];

    noOfMovableHost = 0;
    noOfMovableLowLSpHost = 0;
    for (int i=0; i<NoHost; i++)
    {
        bestLSpforHost[i] = 0.0;
        bestLSpAPforHost[i] = -1;
        for(int j=0; j<HIActive[i].NoConAP; j++)
                {
                    if(AP_HostLinkSpeed[HIActive[i].ConAP[j]-1][i] > bestLSpforHost[i])
                    {
                        bestLSpforHost[i] = AP_HostLinkSpeed[HIActive[i].ConAP[j]-1][i];
                        bestLSpAPforHost[i] = HIActive[i].ConAP[j]-1;
                    }
                }


        if(HIActive[i].movable == 1)
            continue;

        if(HIActive[i].NoConAP > 1 )
            {
                movableHost[noOfMovableHost]=i;
                noOfMovableHost++;

               // if(HIActive[i].AssocAP_HostLinkSpeed != bestLSpforHost[i])
               //     noOfMovableLowLSpHost++;
            }


    }


    if(noOfMovableHost > 0)
    {

        for(int k=0; (k<LOOP_COUNT_HILL_CLIMB_LB_TX_TIME)  ; k++)
        {

            tempMaxTxTime = Local_Sesrch_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();

            if(tempMaxTxTime < globalMaxTxTime)
            {
                globalMaxTxTime = tempMaxTxTime;

                SaveSolution(AIActive, AITempSol, HIActive, HITempSol);

            }
            noOfMovableLowLSpHost = 0;
            for (int i=0; i<NoHost; i++)
            {
                if(HIActive[i].movable == 1)
                    continue;
                if( (HIActive[i].NoConAP > 1) && (HIActive[i].AssocAP_HostLinkSpeed != bestLSpforHost[i]) )
                {
                    movableLowLSpHosts[noOfMovableLowLSpHost] = i;
                    noOfMovableLowLSpHost++;
                }
            }


            // Move all the movable hosts (which are not associated to the best host) to the best host
            for(int i = 0; i < noOfMovableLowLSpHost; i++)
            {

                curHost = movableLowLSpHosts[i];  // randomly select a movable host


                curAP = bestLSpAPforHost[curHost];
                AIActive[curAP].NoConHost++;
                AIActive[curAP].ConHost[AIActive[curAP].NoConHost-1]=curHost+1;

                // Remove the host from the list of associated hosts of the prev AP
                tempFlag=0;
                for(int j=0; j< AIActive[HIActive[curHost].AssocAP-1].NoConHost; j++)
                {
                    if(tempFlag == 1) AIActive[HIActive[curHost].AssocAP-1].ConHost[j-1] = AIActive[HIActive[curHost].AssocAP-1].ConHost[j];
                    if(AIActive[HIActive[curHost].AssocAP-1].ConHost[j] == curHost+1) tempFlag = 1;
                }
                AIActive[HIActive[curHost].AssocAP-1].NoConHost--;

                HIActive[curHost].AssocAP = curAP+1;
                //distanceBtwAP_Host = distance( HIActive[curHost].PositionX, HIActive[curHost].PositionY, AIActive[curAP].PositionX, AIActive[curAP].PositionY);
                HIActive[curHost].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[curAP][curHost];
                //calculateAP_HostLinkSpeed(distanceBtwAP_Host);
            }


            for(int i = 0; i < noOfMovableHost*HILL_CLIMB_MUTATION_FACTOR/100; i++)
            {

                curHost = movableHost[rand() % noOfMovableHost];  // randomly select a movable host
                do
                {
                    //srand ( time(NULL) );
                    curAP = HIActive[curHost].ConAP[rand() % HIActive[curHost].NoConAP]-1; // randomly select an AP among the associable Active APs for the movable host
                }while(curAP == (HIActive[curHost].AssocAP-1));

                AIActive[curAP].NoConHost++;
                AIActive[curAP].ConHost[AIActive[curAP].NoConHost-1]=curHost+1;

                // Remove the host from the list of associated hosts of the prev AP
                tempFlag=0;
                for(int j=0; j< AIActive[HIActive[curHost].AssocAP-1].NoConHost; j++)
                {
                    if(tempFlag == 1) AIActive[HIActive[curHost].AssocAP-1].ConHost[j-1] = AIActive[HIActive[curHost].AssocAP-1].ConHost[j];
                    if(AIActive[HIActive[curHost].AssocAP-1].ConHost[j] == curHost+1) tempFlag = 1;
                }
                AIActive[HIActive[curHost].AssocAP-1].NoConHost--;
                // Change the new AP as the associated AP for the host
                HIActive[curHost].AssocAP = curAP+1;
                //distanceBtwAP_Host = distance( HIActive[curHost].PositionX, HIActive[curHost].PositionY, AIActive[curAP].PositionX, AIActive[curAP].PositionY);
                HIActive[curHost].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[curAP][curHost];
                //calculateAP_HostLinkSpeed(distanceBtwAP_Host);


            } // End of mutation phase
        } // End of Hill-climbing for loop
        //if(needToadjust==0)
        SaveSolution(AITempSol, AIActive, HITempSol, HIActive);

    }


}


float Local_Sesrch_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP()
{

    int curHost,curAP;
    float AP_TxTime[NoAP], maxTxTime, newMaxTxTime;
    int AP_withMaxTxTime, newAP_withMaxTxTime, noOfMovableHostsForMaxTxTimeAP, listOfMovableHostsForMaxTxTimeAP[NoHost]; // all uses index of APs and hosts
    int tempFlag;
    float tempLinkSpeedA, tempLinkSpeedB;
    float distanceBtwAP_Host;

    // Initially calculate expected link speed for each AP-Host link
    for (int i=0; i<NoHost; i++)
    {
        //distanceBtwAP_Host = distance(HIActive[i].PositionX, HIActive[i].PositionY, AIActive[HIActive[i].AssocAP-1].PositionX, AIActive[HIActive[i].AssocAP-1].PositionY);
        HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP-1][i];
        //calculateAP_HostLinkSpeed(distanceBtwAP_Host);
    }



    maxTxTime = -0.1; // initialize maxTxTime and AP_withMaxTxTime
    AP_withMaxTxTime = -1;

    for(int i=0; i<NoAP; i++)
    {
        if(AIActive[i].participateInSelection == 0)
            continue;
        AP_TxTime[i] = 0.0; // initialize to 0 to ommit garbage value

        if(AIActive[i].ifActive == 1)  // consider only active APs
        {
            AP_TxTime[i] = calculateTxTimeForAP(i);

            // track if the new TxTime in maximum
            if(AP_TxTime[i] > maxTxTime)
            {
                maxTxTime = AP_TxTime[i];
                AP_withMaxTxTime = i;
            }
        }
    }

    // ** Generate the list of movable hosts for the AP with Max Tx time
    noOfMovableHostsForMaxTxTimeAP = 0;
    for (int i=0; i<AIActive[AP_withMaxTxTime].NoConHost; i++)
    {
        if(HIActive[AIActive[AP_withMaxTxTime].ConHost[i]-1].NoConAP > 1)
            {
                listOfMovableHostsForMaxTxTimeAP[noOfMovableHostsForMaxTxTimeAP] = AIActive[AP_withMaxTxTime].ConHost[i]-1;
                noOfMovableHostsForMaxTxTimeAP ++;
            }
    }

    for( int LoopCount=0; (LoopCount<LOOP_COUNT_LB_TX_TIME) && (noOfMovableHostsForMaxTxTimeAP > 0); LoopCount++)   // Run the loop for a defined times
    {

        curHost = listOfMovableHostsForMaxTxTimeAP[rand() % noOfMovableHostsForMaxTxTimeAP];  // randomly select a movable host from the list of movable hosts for the AP with Max Tx time

        do
        {
            //srand ( time(NULL) );
            curAP = HIActive[curHost].ConAP[rand() % HIActive[curHost].NoConAP]-1; // randomly select an AP among the associable Active APs for the movable host
        }while(curAP == HIActive[curHost].AssocAP-1);     // check if the new AP is not the former one


        AP_TxTime[AP_withMaxTxTime] = AP_TxTime[AP_withMaxTxTime] - ( (1 / HIActive[curHost].AssocAP_HostLinkSpeed) * HIActive[curHost].HostActiveRate );

        tempLinkSpeedA = AP_HostLinkSpeed[curAP][curHost];

        AP_TxTime[curAP] = AP_TxTime[curAP] + ( (1 / tempLinkSpeedA) * HIActive[curHost].HostActiveRate );

        newMaxTxTime = -0.1; // find new maxTxTime and new AP_withMaxTxTime
        newAP_withMaxTxTime = -1;

        for(int j=0; j<NoAP; j++)
        {
            if(AIActive[j].participateInSelection == 0)
            continue;
            if(AIActive[j].ifActive == 1)  // consider only active APs
            {
                //AP_TxTime[j] = calculateTxTimeForAP(j);
                if(AP_TxTime[j] > newMaxTxTime)
                {
                    newMaxTxTime = AP_TxTime[j];
                    newAP_withMaxTxTime = j;
                }
            }
        }

        if(newMaxTxTime <= maxTxTime)       // Case: if better result found
        {
            AIActive[curAP].NoConHost++;
            AIActive[curAP].ConHost[AIActive[curAP].NoConHost-1]=curHost+1;
            tempFlag=0;
            for(int j=0; j< AIActive[AP_withMaxTxTime].NoConHost; j++)
            {
                if(tempFlag == 1) AIActive[AP_withMaxTxTime].ConHost[j-1] = AIActive[AP_withMaxTxTime].ConHost[j];

                if(AIActive[AP_withMaxTxTime].ConHost[j] == curHost+1) tempFlag = 1;
            }

            //AIActive[HIActive[curHost].AssocAP-1].NoConHost--;
            AIActive[AP_withMaxTxTime].NoConHost--;

            // Change the new AP as the associated AP for the host
            HIActive[curHost].AssocAP = curAP+1;
            HIActive[curHost].AssocAP_HostLinkSpeed = tempLinkSpeedA;
            //HINew[curHost].AssocAP = curAP+1;

            // Select new TxTime and AP as max Tx time & AP
            maxTxTime = newMaxTxTime;
            AP_withMaxTxTime = newAP_withMaxTxTime;
      //      printf("\nnew MaxTxTimeAP : %d , MaxTxTime : %f", AP_withMaxTxTime+1, maxTxTime);

            // ** ReGenerate the list of movable hosts for the AP with Max Tx time
            noOfMovableHostsForMaxTxTimeAP = 0;
            for (int j=0; j<AIActive[AP_withMaxTxTime].NoConHost; j++)
            {
                if(HIActive[AIActive[AP_withMaxTxTime].ConHost[j]-1].NoConAP > 1)
                {
                    listOfMovableHostsForMaxTxTimeAP[noOfMovableHostsForMaxTxTimeAP] = AIActive[AP_withMaxTxTime].ConHost[j]-1;
                    noOfMovableHostsForMaxTxTimeAP ++;
                }
            }


        }
        else                                // case: not better result
        {

            AP_TxTime[AP_withMaxTxTime] = AP_TxTime[AP_withMaxTxTime] + ( (1 / HIActive[curHost].AssocAP_HostLinkSpeed) * HIActive[curHost].HostActiveRate );
            AP_TxTime[curAP] = AP_TxTime[curAP] - ( (1 / tempLinkSpeedA) * HIActive[curHost].HostActiveRate );

        }




    }
    return maxTxTime;

}


void TEST_NEAREST_AP_HOST_ASSOCIATION()
{
    int AP_maxLinkSpeed;
    float distanceBtwAP_Host, maxLinkSpeed, tempLinkSpeed;

    for(int i = 0; i < NoAP; i++)    if(AIActive[i].ifActive == 1)        AIActive[i].NoConHost = 0;
    for(int i = 0; i < NoHost; i++)    HIActive[i].AssocAP = -1;

    for(int i = 0; i < NoHost; i++)
    {
        AP_maxLinkSpeed = -1;
        maxLinkSpeed = -0.1;

        for(int j = 0; j < HIActive[i].NoConAP; j++)
        {

            tempLinkSpeed = AP_HostLinkSpeed[HIActive[i].ConAP[j]-1][i];

            if(tempLinkSpeed > maxLinkSpeed)
            {
                maxLinkSpeed = tempLinkSpeed;
                AP_maxLinkSpeed = HIActive[i].ConAP[j]-1;
            }
        }

        AIActive[AP_maxLinkSpeed].ConHost[AIActive[AP_maxLinkSpeed].NoConHost] = i+1;
        AIActive[AP_maxLinkSpeed].NoConHost ++;

        // change the host info
        HIActive[i].AssocAP = AP_maxLinkSpeed +1;
        HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[AP_maxLinkSpeed][i];
        //printf("HIActive[%d].AssocAP=%d\n",i,HIActive[i].AssocAP);

    }

}


void phase_AP_host_association_optimization()
{
TEST_NEAREST_AP_HOST_ASSOCIATION(); // make a list of movable hosts
PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();//randomly associte removable host to other APs
           /* for(int i=0; i<NoAP; i++)
            {

              if (AIActive[i].ifActive == 1)
              {
                  printf("AIActive[i].ifActive=%d\t %d\n",i+1,AIActive[i].NoConHost);
              }
            }
            exit(1);*/
}

void phase_additional_AP_activation()
{
    int j,k,l;

    int curHost,curAP;
    int noOfActiveAp;

    int listOfActiveAP[NoAP], listOfOFFActiveAP[NoAP], NoOfOFFActiveAP, APToDeactivate, bestFoundNoOfActiveAP; // AP # index starts from 0
    float bestFoundMaxTxTime, newMaxTxTime, APSumLinkSpeed, newAPSumLinkSpeed, offSumLinkSpeed, onSumLinkSpeed;
    int tempNoOfHost;

    int noOfHostInDeactiveAP, listOfHostInDeactiveAP[NoHost]; // Host index starts from 0
    int ifReAssociated[NoHost], ifAllReassociated = 0;// 0: the host of deactivated AP not yet reassociated, 1: Reassociated already

    int bestAlternateAP, bestAlternateOFFInactiveAP, bestAlternateONInactiveAP, bestAlternateInactiveAP; // AP with max # of hosts among the candidate APs

    int noOfRestOfHostInDeactiveAP, listOfRestOfHostInDeactiveAP[NoHost], newNoOfRestOfHostInDeactiveAP, newListOfRestOfHostInDeactiveAP[NoHost]; // Host index starts from 0
    int noOfCommonHosts, bestNoOfOFFCommonHosts, bestNoOfONCommonHosts, bestNoOfCommonHosts;
    int listOfCommonHosts[NoHost], bestListOfOFFCommonHosts[NoHost], bestListOfONCommonHosts[NoHost], bestListOfCommonHosts[NoHost];

    int noOfNewActiveAPs, ListOfNewActiveAPs[NoAP];

    int flagNoInactiveAPFound = 0,flagOFFAPFound = 0;

    int APSelectionflag[NoAP];
    float tempDistance;

    int minNoOfAPsNeeded; // to track the number of APs needed to meet the goal of AverageHostThroughputThreshold
    int flagFirstTimeOptimization = 1;

    int noOfNonActiveAp, NoOfOFFNonActiveAP,NoOfONNonActiveAP,noOfNonActiveAp2, NoOfOFFNonActiveAP2,NoOfONNonActiveAP2;
    int listOfNonActiveAP[NoAP],listOfOFFNonActiveAP[NoAP],listOfONNonActiveAP[NoAP],listOfNonActiveAP2[NoAP],listOfOFFNonActiveAP2[NoAP],listOfONNonActiveAP2[NoAP];
    int APToActivate;

    float oldMaxTxTime, delMaxTxTime, delThroughput; //


    noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)    if (AIActive[i].ifActive == 1)       noOfActiveAp++;

    bestFoundNoOfActiveAP = noOfActiveAp;
    bestFoundMaxTxTime = calculateMaxTxTimeAmongAPs();
    SaveSolution(AIActive, AIBestSol, HIActive, HIBestSol);
    for(int i=0; i<NoAP; i++)
        {
        if(AIActive[i].participateInSelection == 0)
            continue;
        APSelectionflag[i] = 0;
        }

    do
    {
        for(int loopCount = 0; loopCount < LOOP_COUNT_AP_SELECTION_OPTIMIZATION; loopCount++)
        {
          do
          {
            noOfActiveAp = 0;
            NoOfOFFActiveAP = 0;
            for(int i=0; i<NoAP; i=i+2)
            {
            if(AIActive[i].participateInSelection == 0)
            continue;
              if (AIActive[i].ifActive == 1)
              {
                  listOfActiveAP[noOfActiveAp] = i;
                  noOfActiveAp++;
                  if(APSelectionflag[i] == 0)
                  {
                      listOfOFFActiveAP[NoOfOFFActiveAP] = i; // 2.4 ghz AP list
                      NoOfOFFActiveAP ++;
                  }

              }
            }

             // edit start 19/08/21
            int nop=0, n5ap=0;
            int listof5Onap[NoAP];
            for(int i = 1; i < NoAP; i=i+2)
            {
                 if(AIActive[i].participateInSelection == 0)
            continue;
                if(AIActive[i].ifActive == 1)

                {
                  listOfActiveAP[noOfActiveAp] = i;
                  noOfActiveAp++;

                //if(AIActive[i+1].ifActive == 0)
                if(APSelectionflag[i] == 0)

                    {
                        listof5Onap[n5ap]=i;   // 5GHz NIC list
                        n5ap++;
                    }
                }

            }
// if Got 5GHz NIC then deactivate this NIC otherwise deactivate the 2.4GHz
            if(n5ap>0)
            {
                APToDeactivate=listof5Onap[rand() % n5ap];

            }
            else

           {
             APToDeactivate = listOfOFFActiveAP[rand() % NoOfOFFActiveAP];
           }
            // edit end 19/08/21
            noOfHostInDeactiveAP = AIActive[APToDeactivate].NoConHost;

          // printf("Part1 Ap deactive=%d\t %d\n",APToDeactivate+1,noOfHostInDeactiveAP);


            for(int i=0; i<AIActive[APToDeactivate].NoConHost; i++)
            {
                listOfHostInDeactiveAP[i] = AIActive[APToDeactivate].ConHost[i]-1;
                ifReAssociated[i] = 0;
            }
            AIActive[APToDeactivate].ifActive = 0;
            AIActive[APToDeactivate].NoConHost=0;
            APSelectionflag[APToDeactivate] = 1;

            for(int i=0; i<NoHost; i++)
            {
                flag = 0;
                for( j=0; j<HIActive[i].NoConAP; j++)
                {
                    if(flag == 1)
                    {
                        HIActive[i].ConAP[j-1] = HIActive[i].ConAP[j];
                        HIActive[i].AP_HostLinkSpeed[j-1] = HIActive[i].AP_HostLinkSpeed[j];
                    }
                    if(HIActive[i].ConAP[j] == (APToDeactivate+1))  flag = 1;
                }
                if(flag == 1) HIActive[i].NoConAP--;
            }
            for(int i=0; i<noOfHostInDeactiveAP; i++)
            {
                    curHost = listOfHostInDeactiveAP[i];

                    tempNoOfHost = 0; // Here used to track the # of hosts among the candidate active APs
                    bestAlternateAP = -1; // Initializing best AP : AP with max # of hosts among the candidate APs
                    for( j=0; j<HIActive[curHost].NoConAP; j=j+1) // search for other associable Active APs
                    {
                        curAP = HIActive[curHost].ConAP[j]-1;
                        if (AIActive[curAP].ifActive == 1)
                        {
                            ifReAssociated[i] = 1;
                            if(AIActive[curAP].NoConHost >= tempNoOfHost)
                            {
                                tempNoOfHost = AIActive[curAP].NoConHost;
                                bestAlternateAP = curAP;
                            }
                        }
                    }

                    if(ifReAssociated[i] != 0)
                    {

                        // Add this host at the end of the host list of new AP
                        AIActive[bestAlternateAP].NoConHost++;
                        AIActive[bestAlternateAP].ConHost[AIActive[bestAlternateAP].NoConHost-1] = curHost+1;

                        // Change the new AP as the associated AP for the host
                        HIActive[curHost].AssocAP = bestAlternateAP+1;
                        //distanceBtwAP_Host = distance( HIActive[curHost].PositionX, HIActive[curHost].PositionY, AIActive[bestAlternateAP].PositionX, AIActive[bestAlternateAP].PositionY);
                        HIActive[curHost].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[bestAlternateAP][curHost];

                    }
            }

            // Search, if all hosts are reassociated
            ifAllReassociated = 1;
            for(int i=0; i<noOfHostInDeactiveAP; i++)
                if(ifReAssociated[i] == 0)
                {
                    ifAllReassociated = 0;
                    break;
                }


            noOfRestOfHostInDeactiveAP = 0;
            for(int i=0; i<noOfHostInDeactiveAP; i++)
            {
                if(ifReAssociated[i] == 0)
                {
                    listOfRestOfHostInDeactiveAP[noOfRestOfHostInDeactiveAP] = listOfHostInDeactiveAP[i];
                    noOfRestOfHostInDeactiveAP ++;
                }
            }
    noOfNewActiveAPs = 0;
            while(noOfRestOfHostInDeactiveAP != 0)
            {
                bestAlternateInactiveAP = -1;
                bestAlternateOFFInactiveAP = -1;
                bestAlternateONInactiveAP = -1;
                bestNoOfOFFCommonHosts = 0;
                bestNoOfONCommonHosts = 0;
                bestNoOfCommonHosts = 0;
                offSumLinkSpeed = 0.0;
                onSumLinkSpeed = 0.0;

                for(int i=0; i<NoAP; i=i+2)  // choose only 2.4GHz AP
               //for(int i=0; i<NoAP; i++) // for all AP
                {
                    if(AIActive[i].participateInSelection == 0)
                        continue;
                    if(AIActive[i].ifActive == 0)
                    {
                        noOfCommonHosts = 0;//No InActive AP found
                        for( j=0; j<AINew[i].NoConHost; j++) // compare each hosts of current inactive AP
                        {
                            for(int k=0; k<noOfRestOfHostInDeactiveAP; k++)  // with hosts who are not yet assigned
                            {
                                if(listOfRestOfHostInDeactiveAP[k] == (AINew[i].ConHost[j]-1)) // Count # of such common hosts and make lists
                                {
                                    listOfCommonHosts[noOfCommonHosts] = listOfRestOfHostInDeactiveAP[k];
                                    noOfCommonHosts++;
                                }
                            }

                        }
//printf("noOfCommonHosts=%d\n",noOfCommonHosts);
//exit(1);

                        newAPSumLinkSpeed = 0.0;
                        for( j=0; j<noOfCommonHosts; j++)   // total host in input file
                        {
                        newAPSumLinkSpeed = newAPSumLinkSpeed + AP_HostLinkSpeed[i][listOfCommonHosts[j]];
                        }

                        if( APSelectionflag[i] == 0 ) // check if this AP can associate max # of unassociated hosts  // for all AP APSelectionflag[i] = 0
                        {                                         // keep track of the list of hosts ita can associate
                            if( noOfCommonHosts > bestNoOfOFFCommonHosts )   //bestNoOfOFFCommonHosts=0   //in this loop activate new AP
                            {
                                bestNoOfOFFCommonHosts = noOfCommonHosts;
                                for(int k=0; k<noOfCommonHosts; k++)
                                {bestListOfOFFCommonHosts[k] = listOfCommonHosts[k];
                                 //printf("bestListOfOFFCommonHosts[%d]=%d\n",k,bestListOfOFFCommonHosts[k]);
                                }
                                bestAlternateOFFInactiveAP = i;

                                offSumLinkSpeed = newAPSumLinkSpeed;
                         // printf("Part 1 bestAlternateOFFInactiveAP=%d\n",bestAlternateOFFInactiveAP+1);
                            }
                            else if(noOfCommonHosts == bestNoOfOFFCommonHosts)
                            {
                                if(newAPSumLinkSpeed > offSumLinkSpeed)
                                {
                                    bestNoOfOFFCommonHosts = noOfCommonHosts;
                                    for(int k=0; k<noOfCommonHosts; k++)    bestListOfOFFCommonHosts[k] = listOfCommonHosts[k];
                                    bestAlternateOFFInactiveAP = i;
                                    offSumLinkSpeed = newAPSumLinkSpeed;
                               // printf("Part1 Else AlternateOFFInactiveAP=%d\n",bestAlternateOFFInactiveAP+1);
                                }
                            }

                        }
                        if(APSelectionflag[i] == 1) // check if this AP can associate max # of unassociated hosts    // For randomly dective AP set APSelectionflag[i] = 1
                        {                                         // keep track of the list of hosts ita can associate
                            if (noOfCommonHosts > bestNoOfONCommonHosts)
                            {
                                bestNoOfONCommonHosts = noOfCommonHosts;
                                for(int k=0; k<noOfCommonHosts; k++)    bestListOfONCommonHosts[k] = listOfCommonHosts[k];
                                bestAlternateONInactiveAP = i;
                                //printf("Part1 flag1  bestAlternateONInactiveAP=%d\n",bestAlternateONInactiveAP+1);
                                onSumLinkSpeed = newAPSumLinkSpeed;

                            }
                            else if(noOfCommonHosts == bestNoOfONCommonHosts)
                            {
                                if(newAPSumLinkSpeed > onSumLinkSpeed)
                                {
                                    bestNoOfONCommonHosts = noOfCommonHosts;
                                    for(int k=0; k<noOfCommonHosts; k++)    bestListOfONCommonHosts[k] = listOfCommonHosts[k];
                                    bestAlternateONInactiveAP = i;
                                 //   printf("Part1 flag1 Else bestAlternateONInactiveAP=%d\n",bestAlternateONInactiveAP+1);
                                    onSumLinkSpeed = newAPSumLinkSpeed;
                                }
                            }


                        }

                    }
                       //printf("APSelectionflag[%d]=%d\n",i,APSelectionflag[i]);

                }
                if(bestAlternateOFFInactiveAP != -1)
                {
                    bestAlternateInactiveAP = bestAlternateOFFInactiveAP;
                    bestNoOfCommonHosts = bestNoOfOFFCommonHosts;
                    for(int k=0; k<bestNoOfOFFCommonHosts; k++) bestListOfCommonHosts[k] = bestListOfOFFCommonHosts[k];

                    ListOfNewActiveAPs[noOfNewActiveAPs] = bestAlternateInactiveAP;
                    noOfNewActiveAPs++;
                }
                else if(bestAlternateONInactiveAP != -1)
                {
                    bestAlternateInactiveAP = bestAlternateONInactiveAP;
                    bestNoOfCommonHosts = bestNoOfONCommonHosts;
                    for(int k=0; k<bestNoOfONCommonHosts; k++) bestListOfCommonHosts[k] = bestListOfONCommonHosts[k];
                }
                else
                {
                    flagNoInactiveAPFound = 1;
                }

                // Set the selection flag to 1
                APSelectionflag[bestAlternateInactiveAP] = 1;

                // Activate the selected inactive AP
                AIActive[bestAlternateInactiveAP].ifActive = 1;
                AIActive[bestAlternateInactiveAP].NoConHost=0;
                for(int i=0; i<NoHost; i++) // Update the info of list of connectible Active APs in the hosts info
                    for( j=0; j<HINew[i].NoConAP; j++)
                        if( HINew[i].ConAP[j] == (bestAlternateInactiveAP+1))
                            {
                                HIActive[i].ConAP[HIActive[i].NoConAP] = bestAlternateInactiveAP+1;
                                HIActive[i].AP_HostLinkSpeed[HIActive[i].NoConAP-1] = AP_HostLinkSpeed[bestAlternateInactiveAP][i];
                                HIActive[i].NoConAP++;
                                break;
                            }
                // Associate the hosts in the list to the selected best AP
                for(int i=0; i<bestNoOfCommonHosts; i++)
                {
                    curHost = bestListOfCommonHosts[i];
                    AIActive[bestAlternateInactiveAP].ConHost[AIActive[bestAlternateInactiveAP].NoConHost] = curHost+1;
                    AIActive[bestAlternateInactiveAP].NoConHost ++;
                    HIActive[curHost].AssocAP = bestAlternateInactiveAP+1;
                    HIActive[curHost].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[bestAlternateInactiveAP][curHost];
                    }

                // Make a new list Of Rest Of Hosts In Deactive AP
                newNoOfRestOfHostInDeactiveAP = 0;
                for(int i=0; i<noOfRestOfHostInDeactiveAP; i++)
                {
                    flag = 0;
                    for( j=0; j<bestNoOfCommonHosts; j++)
                        if(listOfRestOfHostInDeactiveAP[i] == bestListOfCommonHosts[j])
                        {
                            flag = 1;
                            break;
                        }

                    if(flag == 0)
                    {
                        newListOfRestOfHostInDeactiveAP[newNoOfRestOfHostInDeactiveAP] = listOfRestOfHostInDeactiveAP[i];
                        newNoOfRestOfHostInDeactiveAP++;
                    }
                }

                // Replace the new list to original list
                noOfRestOfHostInDeactiveAP = newNoOfRestOfHostInDeactiveAP;
                for(int i=0; i<newNoOfRestOfHostInDeactiveAP; i++)  listOfRestOfHostInDeactiveAP[i] = newListOfRestOfHostInDeactiveAP[i];
        }
        // end of first while loop
               /* for(int i=0; i<NoAP; i++)
                {
                    if (AIActive[i].ifActive == 1)
                    {
                        printf("Best alternat AP AIActive[i].ifActive =%d \t %d\t flag= %d \n",i+1,AIActive[i].NoConHost,APSelectionflag[i] );
                    }
                }*/
            // exit(1);

            noOfActiveAp = 0;
            for(int i=0; i<NoAP; i++)
            {
            if(AIActive[i].participateInSelection == 0)
            continue;
              if (AIActive[i].ifActive == 1)
              {
                  listOfActiveAP[noOfActiveAp] = i;
                  noOfActiveAp++;
              }
            }
            if( (flagFirstTimeOptimization == 0) && (noOfActiveAp < minNoOfAPsNeeded))
            {

                    noOfNonActiveAp = 0;
                    NoOfOFFNonActiveAP = 0;
                    NoOfONNonActiveAP = 0;
                   noOfNonActiveAp2 = 0;
                    NoOfOFFNonActiveAP2 = 0;
                    NoOfONNonActiveAP2 = 0;

                // edit start 19/08/21
                    for(int i=0; i<NoAP; i=i+1)
                    {
                        int j=i+1;
                        if(AIActive[i].participateInSelection == 0)
                            continue;
                        if ((i%2==0) && AIActive[i].ifActive==1 && AIActive[j].ifActive==0)  // slect 5 GHz
                        {
                            listOfNonActiveAP[noOfNonActiveAp] = j;
                            noOfNonActiveAp++;
                            if(APSelectionflag[j] == 0)
                            {
                                 listOfOFFNonActiveAP[NoOfOFFNonActiveAP] = j; // list 5GHz where 2.4GHz AP Active
                                 NoOfOFFNonActiveAP ++;
                            }
                            else
                            {
                                listOfONNonActiveAP[NoOfONNonActiveAP] = j;
                                NoOfONNonActiveAP ++;
                            }

                        }
                        else if ( (i%2)==0 && AIActive[i].ifActive == 0)
                        //if ((i%2==0) && (AIActive[i].ifActive == 0))  // select 2.4 GHz
                        {
                            listOfNonActiveAP[noOfNonActiveAp] = i;
                            noOfNonActiveAp++;
                            if(APSelectionflag[i] == 0)
                            {
                              listOfOFFNonActiveAP[NoOfOFFNonActiveAP] = i;  // 2.4GHz list
                            NoOfOFFNonActiveAP ++;
                            }
                            else
                            {
                                listOfONNonActiveAP[NoOfONNonActiveAP] = i; //  2.4GHz AP list
                                NoOfONNonActiveAP++;
                            }

                        }

                    }

                    if(NoOfOFFNonActiveAP != 0)
                {                                        // randomly select an OFF non-active AP
                    APToActivate = listOfOFFNonActiveAP[rand() % NoOfOFFNonActiveAP];
              //  printf("Part1 flagoptimiza if  ToActivate===================================%d\n",APToActivate+1);
                    ListOfNewActiveAPs[noOfNewActiveAPs] = APToActivate;  // not done if ON non-active AP is selected
                    noOfNewActiveAPs++;
                }
                else
                {
                    APToActivate = listOfONNonActiveAP[rand() % NoOfONNonActiveAP];
                  //printf("Part1 flagoptimiza  ToActivate=------------------------%d\n",APToActivate+1);

                }
                // edit end 19/08/21
                    // Activate the selected non-active AP
                    AIActive[APToActivate].ifActive = 1;
                    AIActive[APToActivate].NoConHost=0;
                    APSelectionflag[APToActivate] = 1;
                    //printf("\n\n P1 Flag o AP %d activated\n",APToActivate+1);

                //  printf("Part1 flag0 active=%d\n",APToActivate+1);
                    for(int i=0; i<NoHost; i++) // Update the info of list of connectible Active APs in the hosts info
                        for( j=0; j<HINew[i].NoConAP; j++)
                            if( HINew[i].ConAP[j] == (APToActivate+1))
                            {
                                HIActive[i].ConAP[HIActive[i].NoConAP] = APToActivate+1;
                                HIActive[i].AP_HostLinkSpeed[HIActive[i].NoConAP-1] = AP_HostLinkSpeed[APToActivate][i];
                                HIActive[i].NoConAP++;
                                break;
                            }

            }

            for(int i=0; i<noOfNewActiveAPs; i++) APSelectionflag[ListOfNewActiveAPs[i]] = 0;

            noOfActiveAp = 0;
            for(int i=0; i<NoAP; i++)
            {
            if(AIActive[i].participateInSelection == 0)
            continue;
              if (AIActive[i].ifActive == 1)
              {
                  listOfActiveAP[noOfActiveAp] = i;
                  //printf("i=%d \n ",i+1);
                  noOfActiveAp++;
              }
            }

            if(noOfActiveAp <= bestFoundNoOfActiveAP)
            {

                TEST_NEAREST_AP_HOST_ASSOCIATION();
                PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();

                newMaxTxTime = calculateMaxTxTimeAmongAPs();

                if( (noOfActiveAp < bestFoundNoOfActiveAP) || (newMaxTxTime < bestFoundMaxTxTime))  // Lead to a better state
                {
                   bestFoundNoOfActiveAP = noOfActiveAp;
                    bestFoundMaxTxTime = newMaxTxTime;
                    //if(needToadjust==0)
                    SaveSolution(AIActive, AIBestSol, HIActive, HIBestSol);

                }
                else
                {
                    //if(needToadjust==0)
                    SaveSolution(AIBestSol, AIActive, HIBestSol, HIActive);

               }
                // *****************************************************************

            }
            else
            {
                TEST_NEAREST_AP_HOST_ASSOCIATION();
                PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();

                newMaxTxTime = calculateMaxTxTimeAmongAPs();
                if(newMaxTxTime < bestFoundMaxTxTime)
                   {
                        bestFoundNoOfActiveAP = noOfActiveAp;
                    bestFoundMaxTxTime = newMaxTxTime;
                   }

                //if(needToadjust==0)
                SaveSolution(AIBestSol, AIActive, HIBestSol, HIActive);

            }
            flagOFFAPFound = 0;
            /*int pairap=1;
            for(int i=0;i<NoAP;i++)
            {
                if(AIActive[i].participateInSelection == 0)
                continue;
                if(pairap==1)
                   {
                      printf("ACtive AP1===================%d\n",pairap);

                       flagOFFAPFound=2;
                       break;
                   }
                   else if((APSelectionflag[i] == 0)&&(AIActive[i].ifActive == 1))
                    {
                    flagOFFAPFound = 1;
                    break;
                    }

            }*/
           float res=1/bestFoundMaxTxTime;
           // printf("Result=------------------------------%f\n",res);
            // edit start 19/08/21
            for(int i=0;i<NoAP;i++)
            {
                if(AIActive[i].participateInSelection == 0)
                continue;
                if((i%2==0) && (AIActive[i].ifActive== AIActive[i+1].ifActive) && (res<AverageHostThroughputThreshold))
                   {
                     // printf("ACtive AP===================%d\t %d\n",i+1,i+2);

                       flagOFFAPFound=1;
                      break;
                   }
                  // else if((APSelectionflag[i] == 0)&&(AIActive[i].ifActive == 1))
                  else if((APSelectionflag[i] == 0)&&(AIActive[i].ifActive == 1)&& (res<AverageHostThroughputThreshold))
                    {
                       // printf("----------ACtive AP2===================%d\t %d\n",i+1,i+2);
                    flagOFFAPFound = 2;
                    break;
                    }

            }
            // edit end 19/08/21

            /*flagOFFAPFound = 0;
            for(int i=0; i<NoAP; i++)
                {
                if(AIActive[i].participateInSelection == 0)
                continue;
                if((APSelectionflag[i] == 0)&&(AIActive[i].ifActive == 1))
                    {
                    flagOFFAPFound = 1;
                    break;
                    }
                }*/

          }while(flagOFFAPFound == 2);


        int noOfActiveAPs=0, noOfActiveAPsToChange, ActiveAPChangeCounter;

        for(int i=0; i<NoAP; i++)
        {
        if(AIActive[i].participateInSelection == 0)
            continue;
            APSelectionflag[i] = 0;
        }

        //printf("\n\nAll selection flags reassigned to zero\n");

      //  for(int i=0; i<=NoAP; i++)  if(AIActive[i].ifActive == 1)   noOfActiveAPs++;
      //  printf("\n#bestFoundNoOfActiveAP Active APs: ---------------------%d\n",bestFoundNoOfActiveAP);

        }

        if( ((1.0/bestFoundMaxTxTime) < AverageHostThroughputThreshold) && (bestFoundNoOfActiveAP < NoAPAll))
        {
            if(flagFirstTimeOptimization == 1)
            {
                oldMaxTxTime = bestFoundMaxTxTime;

                // save the current best solution as old solution
                SaveSolution(AIBestSol, AIOldBestSol, HIBestSol, HIOldBestSol);
            }
            else
            {

                delThroughput = (1/bestFoundMaxTxTime) - (1/oldMaxTxTime);

                if(delThroughput >= THROUGHPUT_IMPROVE_MARGIN)
                {
                    oldMaxTxTime = bestFoundMaxTxTime;

                    // save the current best solution as old solution
                    SaveSolution(AIBestSol, AIOldBestSol, HIBestSol, HIOldBestSol);
                }
                else
                {
                    SaveSolution(AIOldBestSol, AIBestSol, HIOldBestSol, HIBestSol);

                    break;
                }

            }

            flagFirstTimeOptimization = 0;                  // Change flag of first time
            minNoOfAPsNeeded = bestFoundNoOfActiveAP +1;    // Increase minimum # of APs needed
            //if(needToadjust==0)
            SaveSolution(AIBestSol, AIActive, HIBestSol, HIActive); // load best state as current state.


                noOfNonActiveAp = 0;
                NoOfOFFNonActiveAP = 0;
                NoOfONNonActiveAP = 0;
                NoOfOFFNonActiveAP2=0;
                NoOfONNonActiveAP2=0;
// edit start 19/08/21
          for(int i=0; i<NoAP; i++)
            {
                int k=i+1;
                if(AIActive[i].participateInSelection ==0)
                    continue;
               if ((i%2)==0 && (AIActive[i].ifActive == 1) && (AIActive[k].ifActive == 0))
                   // if ((i%2)==1 && (AIActive[i].ifActive == 0))
                {
                    listOfNonActiveAP[noOfNonActiveAp] = i;
                    noOfNonActiveAp++;
                    if(APSelectionflag[i] == 0)
                    {
                    listOfOFFNonActiveAP[NoOfOFFNonActiveAP] = i;  //5GHz list where 2.4GHz actiive
                    NoOfOFFNonActiveAP ++;

                    }
                }

             else if ((i%2)==0 && (AIActive[i].ifActive == 0))
                {
                    listOfNonActiveAP[noOfNonActiveAp] = i;
                    noOfNonActiveAp++;
                    if(APSelectionflag[i] == 0)
                    {
                       listOfOFFNonActiveAP[NoOfOFFNonActiveAP] = i;  // 2.4GHz list which are inactive
                    NoOfOFFNonActiveAP ++;
                    }
                }
            }
             printf("Average not Fit\n");
            for(int i = 0; i < NoAP; i++)
            {
                if(AIActive[i].ifActive == 1)
                {
                   // printf("AIActive[i].ifActive=%d\n",i+1);
// printf("AIActive[i].identity=%d\n",AIActive[i].identity);
                }
            }
            // edit end 19/08/21
            APToActivate = listOfOFFNonActiveAP[rand() % NoOfOFFNonActiveAP];
                APSelectionflag[APToActivate] = 1;

           //  printf("\n\nAP %d activated\n",APToActivate+1);


                // Activate the selected non-active AP
                AIActive[APToActivate].ifActive = 1;
                AIActive[APToActivate].NoConHost=0;
                //printf("\n\nAP %d activated\n",APToActivate+1);

            for(int i=0; i<NoAP; i++)
            {

                if (AIActive[i].ifActive == 1)
                {
                    //printf("Before AIActive[i].ifActive=%d\t %d \t flag=%d\n",i+1,AIActive[i].NoConHost,APSelectionflag[i]);
                }
            }
                for(int i=0; i<NoHost; i++) // Update the info of list of connectible Active APs in the hosts info
                    for( j=0; j<HINew[i].NoConAP; j++)
                        if( HINew[i].ConAP[j] == (APToActivate+1))
                            {
                                HIActive[i].ConAP[HIActive[i].NoConAP] = APToActivate+1;

                                HIActive[i].AP_HostLinkSpeed[HIActive[i].NoConAP-1] = AP_HostLinkSpeed[APToActivate][i];
                                HIActive[i].NoConAP++;
                                break;
                            }

            TEST_NEAREST_AP_HOST_ASSOCIATION();
            PHASE_RANDOM_MOVE_TO_REDUCE_TX_TIME_FOR_BOTTLENECK_AP();

            newMaxTxTime = calculateMaxTxTimeAmongAPs();
         for(int i=0; i<NoAP; i++)
            {

              if (AIActive[i].ifActive == 1)
              {
                //  printf("after AIActive[i].ifActive=%d\t  %d\t flag= %d\n",i+1,AIActive[i].NoConHost,APSelectionflag[i]);
              }
            }
            bestFoundNoOfActiveAP = minNoOfAPsNeeded;
            bestFoundMaxTxTime = newMaxTxTime;
            SaveSolution(AIActive, AIBestSol, HIActive, HIBestSol);
       }

        else
        {
            if((1.0/bestFoundMaxTxTime) >= AverageHostThroughputThreshold)
            {
                break;

            }

            else if(bestFoundNoOfActiveAP >= NoAPAll)
                {//mnm
                calculateTotalSpeedAmongAPs();

                if(speedOfRAP>totalBandwidth)
                {
                needToadjust = 1;
                adjustedRatio = totalBandwidth/speedOfRAP;
                calculateInitialAP_HostLinkSpeed();

        for(int i=0;i<NoHost;i++)
        {
        for (int j=0; j<HIActive[i].NoConAP; j++)
            {
            if(AIActive[HIActive[i].ConAP[j]-1].ifActive==1 && AIActive[HIActive[i].ConAP[j]-1].type==0)
            {
            HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP-1][i];
            HIActive[i].AP_HostLinkSpeed[HIActive[i].NoConAP-1] = AP_HostLinkSpeed[HINew[i].ConAP[j]-1][i];
            }
            if(AINew[HINew[i].ConAP[j]-1].type==0)
            {
            HI[i].AP_HostLinkSpeed[j]=adjustedRatio*HI[i].AP_HostLinkSpeed[j];
            HINew[i].AP_HostLinkSpeed[j]=adjustedRatio*HINew[i].AP_HostLinkSpeed[j];
            }

            }
        }

                }
                else
                {  //check4error
                }

                if(vAPused == 0 && needToadjust==0)
                    {
                    vAPused = 1;

                    for(int i = 0; i < NoAP; i++)
                    {

                    if(AI[i].type == 1)
                        {
                            AINew[i].participateInSelection = 1;
                            AIActive[i].participateInSelection = 1;
                        }
                    }
                    NoAPAll = NoAPAll+numVAP;
                    }

                else if((vap_1st==0 && needToadjust==1) ||(vap_1st==0 &&needToadjust==0 && numDefectAP!=0))
                    {
                    int tm_ap[100];
                    vap_1st = 1;
                    int cnt_tmp_vap=0;
                    for(int i=0; i<NoAP; i++)
                    {
                    if(AIActive[i].ifActive == 1 && (AIActive[i].type ==0 || AIActive[i].type ==1))  // consider only active APs
                    {
                    float AP_TxTimeRAP;
                    AP_TxTimeRAP = calculateTxTimeForAP(i);
                    if(AP_TxTimeRAP == 0.0)
                    continue;
                    if((1.0/AP_TxTimeRAP) < AverageHostThroughputThreshold)
                    {
                    sortHostinAP(i);
                    makeAcopy(AIActive,AIActive4INC);

                while(1)
                {   int c=0, tap_number=0;
                    tap_number=NoAPReal+ numDefectAP+numVAP+AIActive4INC[i].ConHost[0];
                    tm_ap[cnt_tmp_vap]=tap_number;
                    ++cnt_tmp_vap;
                    for( c = 1; c <AIActive4INC[i].NoConHost;  c++)
                    {
                        AIActive4INC[i].ConHost[c-1] = AIActive4INC[i].ConHost[c];
                    }
                    AIActive4INC[i].ConHost[c-1]='\0';
                    AIActive4INC[i].NoConHost = AIActive4INC[i].NoConHost-1;
                    float AP_TxTimeRAPtmp2 = calTx4APINC(i);
                    if(AP_TxTimeRAPtmp2 != 0.0)
                    {
                    if((1.0/AP_TxTimeRAPtmp2) >= AverageHostThroughputThreshold)
                    {
                    break;
                    }

                    }
                }
            }

        }
    }

    for(int i=0;i<cnt_tmp_vap;i++)
    {
    if(AINew[tm_ap[i]].type==2)
                    {
                    AINew[tm_ap[i]].participateInSelection = 1;
                    AIActive[tm_ap[i]].participateInSelection = 1;
                    }
    }
    NoAPAll = NoAPAll+cnt_tmp_vap;
                        }
                        else
                        break;
                    }

                else
                break;
        }

    }while(1);

    // end of first do loop

    SaveSolution(AIBestSol, AIActive, HIBestSol, HIActive);

    noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].participateInSelection == 0)
        continue;
    if (AIActive[i].ifActive == 1)
        noOfActiveAp++;
    }

    newMaxTxTime = calculateMaxTxTimeAmongAPs();

    flag =0;
    for(int i=0; i<NoAP; i++)
    {
    if(AIActive[i].participateInSelection == 0)
    continue;
    if (AIActive[i].ifActive == 1)
        {
        if(flag == 0)
        {
            flag = 1;
        }
        }
    }

    printf("\n\nBest Found Result\n---------------------------------------------\n%f-%f\n", 1.0/bestFoundMaxTxTime,AverageHostThroughputThreshold);
    printf("\nOptimized List of active APs: \n--------------------------------------\n");

    for(int i=0; i<NoAP; i++)
            {
                if(AIActive[i].ifActive == 1)
                   // printf("%d\", i+1);
                    printf("list ___________________= %d \t %d \t %d\n",i+1,AIActive[i].NoConHost,APSelectionflag[i]);
            }
}


void PostAssociationOptimization()
{

     int temp_i, temp_j, swapAP, ifSwapped, k, l;
     float currentMaxTxTime, newMaxTxTime;

     float oldSum, newSum;

      currentMaxTxTime = calculateMaxTxTimeAmongAPs();

      ifSwapped = 1;
      do
      {
        ifSwapped = 0;

        for( int i=0; i<NoHost; i++)
            {
                if(HIActive[i].movable == 1) continue;
                for( int j=0; j<NoHost; j++)
                {
                    if(HIActive[j].movable == 1) continue;
                    if( (i==j) || (HIActive[i].AssocAP == HIActive[j].AssocAP) ) continue;

                    oldSum = 0.0;
                    newSum = 0.0;

                    oldSum = ( HIActive[i].HostActiveRate / HIActive[i].AssocAP_HostLinkSpeed ) + ( HIActive[j].HostActiveRate / HIActive[j].AssocAP_HostLinkSpeed);
                    newSum = ( HIActive[i].HostActiveRate / AP_HostLinkSpeed[HIActive[j].AssocAP-1][i] ) + ( HIActive[j].HostActiveRate / AP_HostLinkSpeed[HIActive[i].AssocAP-1][j] );
                    if(newSum < oldSum)
                    {
                        temp_i = 0;
                        for(k=0; k<HIActive[i].NoConAP; k++)
                            if(HIActive[i].ConAP[k] == HIActive[j].AssocAP)
                            {
                                temp_i = 1;
                                break;
                            }
                        temp_j = 0;
                        for(k=0; k<HIActive[j].NoConAP; k++)
                            if(HIActive[j].ConAP[k] == HIActive[i].AssocAP)
                            {
                                temp_j = 1;
                                break;
                            }

                        // swap the association of Host i with Host j - if each-other's AP is associable
                        if( (temp_i == 1) && (temp_j == 1))
                        {
                            //printf("\nSwapped here (H%d-AP%d , H%d-AP%d)\n",i+1, HIActive[i].AssocAP, j+1, HIActive[j].AssocAP);

                            // Update APInfo

                            // Update info of AP associated to Host i
                            for(k=0; k<AIActive[HIActive[i].AssocAP-1].NoConHost; k++)
                                if( (AIActive[HIActive[i].AssocAP-1].ConHost[k]) == (i+1))
                                {
                                    AIActive[HIActive[i].AssocAP-1].ConHost[k] = j+1;
                                    break;
                                }
                            // Update info of AP associated to Host j
                            for(l=0; l<AIActive[HIActive[j].AssocAP-1].NoConHost; l++)
                                if( (AIActive[HIActive[j].AssocAP-1].ConHost[l]) == (j+1))
                                {
                                    AIActive[HIActive[j].AssocAP-1].ConHost[l] = i+1;
                                    break;
                                }
                            swapAP = HIActive[i].AssocAP;
                            HIActive[i].AssocAP = HIActive[j].AssocAP;
                            HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP-1][i];
                            HIActive[j].AssocAP = swapAP;
                            HIActive[j].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[j].AssocAP-1][j];
                            newMaxTxTime = calculateMaxTxTimeAmongAPs();
                            if(newMaxTxTime <= currentMaxTxTime)
                            {
                                currentMaxTxTime = newMaxTxTime;
                                ifSwapped = 1;
                            }
                            else if(newMaxTxTime > currentMaxTxTime)
                            {
                                swapAP = HIActive[i].AssocAP;
                                HIActive[i].AssocAP = HIActive[j].AssocAP;
                                HIActive[i].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[i].AssocAP-1][i];
                                HIActive[j].AssocAP = swapAP;
                                HIActive[j].AssocAP_HostLinkSpeed = AP_HostLinkSpeed[HIActive[j].AssocAP-1][j];
                                AIActive[HIActive[i].AssocAP-1].ConHost[k] = i+1;
                                AIActive[HIActive[j].AssocAP-1].ConHost[l] = j+1;
                            }

                        }

                    }


                }
            }
      }while(ifSwapped == 1);
}


void makeAcopy(struct APInfo *FromAIInfo, struct APInfo *ToAIInfo)
{
            for (int i=0;i<NoAP;i++)
            {
                ToAIInfo[i].APID = FromAIInfo[i].APID;
                ToAIInfo[i].PositionX = FromAIInfo[i].PositionX;
                ToAIInfo[i].PositionY = FromAIInfo[i].PositionY;
                ToAIInfo[i].GroupID = FromAIInfo[i].GroupID;

                ToAIInfo[i].NoConHost = FromAIInfo[i].NoConHost;
                for (int j=0;j<FromAIInfo[i].NoConHost;j++)     ToAIInfo[i].ConHost[j] =FromAIInfo[i].ConHost[j];

                ToAIInfo[i].ifActive = FromAIInfo[i].ifActive;
                ToAIInfo[i].HostMargin = FromAIInfo[i].HostMargin;
                ToAIInfo[i].ifSatisfied = FromAIInfo[i].ifSatisfied;

                ToAIInfo[i].nodeID = FromAIInfo[i].nodeID;
                ToAIInfo[i].ChannelID = FromAIInfo[i].ChannelID;
            }

}

void generateOutputAndSimulationInputFiles(const char *phaseName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    int noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)
        {
            if(localAIActive[i].participateInSelection == 0)
            continue;
            if(localAIActive[i].NoConHost == 0)
                continue;
            if (localAIActive[i].ifActive == 1)
            {
                localAIActive[i].nodeID = noOfActiveAp;
                noOfActiveAp++;
            }

        }

    for (int i=0; i<NoHost; i++)
    {
        localHIActive[i].nodeID = noOfActiveAp+i;    // *** Assign Node ID for Hosts here
    }



    strcpy(opFileName, "Output_");
    strcat(opFileName, phaseName);
    strcat(opFileName,ipFileNamePart);
    strcpy(opFileType, ".txt");
    strcat(opFileName,opFileType);

    printOutput(opFileName, localAIActive, localHIActive);

    strcpy(SimulatorInputGeneratorFileName, "SimIPGenInput_");
    strcat(SimulatorInputGeneratorFileName, phaseName);
    strcat(SimulatorInputGeneratorFileName,ipFileNamePart);
    strcpy(SimIPGenInputFileType, ".txt");
    strcat(SimulatorInputGeneratorFileName,SimIPGenInputFileType);
    prepareInputFileForSimulatorInputGenerator(SimulatorInputGeneratorFileName, localAIActive, localHIActive);

    strcpy(DrawAssociationInputFileName, "DrawAssocInput_");
    strcat(DrawAssociationInputFileName, phaseName);
    strcat(DrawAssociationInputFileName,ipFileNamePart);
    strcpy(DrawAssociationInputFileType, ".txt");
    strcat(DrawAssociationInputFileName,DrawAssociationInputFileType);

    //prepareInputFileForPerlProgramToDrawAssociation(DrawAssociationInputFileName, localAIActive, localHIActive);
    // * Generate input files for simulator after AP aggregation before load balancing/throughput optimization


    strcpy(FIELD_infoFileName, "field_");
    strcat(FIELD_infoFileName,phaseName);
    strcat(FIELD_infoFileName,ipFileNamePart);
    strcpy(FIELD_infoFileType, ".dat");
    strcat(FIELD_infoFileName,FIELD_infoFileType);

    //generateFIELD_File(FIELD_infoFileName);


    strcpy(NIC_infoFileName, "nic_");
    strcat(NIC_infoFileName,phaseName);
    strcat(NIC_infoFileName,ipFileNamePart);
    strcpy(NIC_infoFileType, ".dat");
    strcat(NIC_infoFileName,NIC_infoFileType);

    //generateNIC_File(NIC_infoFileName, localAIActive, localHIActive);


    strcpy(NODE_infoFileName, "node");
    //strcat(NODE_infoFileName,phaseName);
    //strcat(NODE_infoFileName,ipFileNamePart);
    strcpy(NODE_infoFileType, ".dat");
    strcat(NODE_infoFileName,NODE_infoFileType);

    //generateNODE_File(NODE_infoFileName, localAIActive, localHIActive);
    //generateNODE_File1(NODE_infoFileName, localAIActive, localHIActive);


    strcpy(ROUTE_infoFileName, "route_");
    strcat(ROUTE_infoFileName,phaseName);
    strcat(ROUTE_infoFileName,ipFileNamePart);
    strcpy(ROUTE_infoFileType, ".dat");
    strcat(ROUTE_infoFileName,ROUTE_infoFileType);

    //generateROUTE_File(ROUTE_infoFileName, localAIActive, localHIActive);

    strcpy(SAP_patternFileName, "sap_");
    strcat(SAP_patternFileName,phaseName);
    strcat(SAP_patternFileName,ipFileNamePart);
    strcpy(SAP_patternFileType, ".dat");
    strcat(SAP_patternFileName,SAP_patternFileType);

}

float calTx4APINC(int AP_index)
{
    float sumTxTime = 0.0;
    float tmpMAP_speed = 30.00;
    float tmpMAPSpeed = 0;

    for(int j=0; j<AIActive4INC[AP_index].NoConHost; j++)
    {
        sumTxTime = sumTxTime + ( HIActive[AIActive4INC[AP_index].ConHost[j]-1].HostActiveRate / HIActive[AIActive4INC[AP_index].ConHost[j]-1].AssocAP_HostLinkSpeed );
    }

    return sumTxTime;
}

void SaveSolution(struct APInfo *FromAIInfo, struct APInfo *ToAIInfo, struct HostInfo *FromHIInfo, struct HostInfo *ToHIInfo)
{
            for (int i=0;i<NoAP;i++)
            {
                ToAIInfo[i].APID = FromAIInfo[i].APID;
                ToAIInfo[i].PositionX = FromAIInfo[i].PositionX;
                ToAIInfo[i].PositionY = FromAIInfo[i].PositionY;
                ToAIInfo[i].GroupID = FromAIInfo[i].GroupID;

                ToAIInfo[i].NoConHost = FromAIInfo[i].NoConHost;
                for (int j=0;j<FromAIInfo[i].NoConHost;j++)     ToAIInfo[i].ConHost[j] =FromAIInfo[i].ConHost[j];

                ToAIInfo[i].ifActive = FromAIInfo[i].ifActive;
                ToAIInfo[i].HostMargin = FromAIInfo[i].HostMargin;
                ToAIInfo[i].ifSatisfied = FromAIInfo[i].ifSatisfied;

                ToAIInfo[i].nodeID = FromAIInfo[i].nodeID;
                ToAIInfo[i].ChannelID = FromAIInfo[i].ChannelID;
            }

            for (int i=0; i<NoHost; i++)
            {
                ToHIInfo[i].HostID = FromHIInfo[i].HostID;
                ToHIInfo[i].PositionX = FromHIInfo[i].PositionX;
                ToHIInfo[i].PositionY = FromHIInfo[i].PositionY;
                ToHIInfo[i].GroupID = FromHIInfo[i].GroupID;
                ToHIInfo[i].HostActiveRate = FromHIInfo[i].HostActiveRate;

                ToHIInfo[i].NoConAP = FromHIInfo[i].NoConAP;

                for (int j=0; j<FromHIInfo[i].NoConAP; j++)
                {
                    ToHIInfo[i].ConAP[j] = FromHIInfo[i].ConAP[j];
                    ToHIInfo[i].AP_HostLinkSpeed[j] = FromHIInfo[i].AP_HostLinkSpeed[j];
                }

                ToHIInfo[i].AssocAP = FromHIInfo[i].AssocAP;
                ToHIInfo[i].AssocAP_HostLinkSpeed = FromHIInfo[i].AssocAP_HostLinkSpeed;

                ToHIInfo[i].NoSat = FromHIInfo[i].NoSat;
                for (int j=0; j<HI[i].NoSat; j++)    HIActive[i].SatAP[j] = FromHIInfo[i].SatAP[j];

                ToHIInfo[i].nodeID = FromHIInfo[i].nodeID;
                ToHIInfo[i].ChannelID = FromHIInfo[i].ChannelID;
            }
}

float calculateTxTimeForAP(int AP_index)
{
    float sumTxTime = 0.0;
    float tmpMAP_speed = 30.00;
    float tmpMAPSpeed = 0;

    for(int j=0; j<AIActive[AP_index].NoConHost; j++)
    {
    if(AIActive[AP_index].type == 2)
    {
    sumTxTime = sumTxTime + ( HIActive[AIActive[AP_index].ConHost[j]-1].HostActiveRate / HIActive[AIActive[AP_index].ConHost[j]-1].AssocAP_HostLinkSpeed );
    tmpMAPSpeed = tmpMAPSpeed + HIActive[AIActive[AP_index].ConHost[j]-1].HostActiveRate / tmpMAP_speed;
    }
    else
    {
        sumTxTime = sumTxTime + ( HIActive[AIActive[AP_index].ConHost[j]-1].HostActiveRate / HIActive[AIActive[AP_index].ConHost[j]-1].AssocAP_HostLinkSpeed );
    }
    if(AIActive[AP_index].type == 2)
        {
        if(tmpMAPSpeed>=sumTxTime)
            {
            sumTxTime = tmpMAPSpeed;
            }
        }
    }

    return sumTxTime;
}

float calculateSumLinkSpeedForAP(int AP_index)
{
    float sumLinkSpeed = 0.0;
    for(int j=0; j<AIActive[AP_index].NoConHost; j++)
    {
        sumLinkSpeed = sumLinkSpeed + HIActive[AIActive[AP_index].ConHost[j]-1].AssocAP_HostLinkSpeed;
    }

    return sumLinkSpeed;
}


float calculateMaxTxTimeAmongAPs()
{
    float maxTxTime,AP_TxTime;

    maxTxTime = -0.1; // initialize maxTxTime and AP_withMaxTxTime

    for(int i=0; i<NoAP; i++)
    {
        if(AIActive[i].ifActive == 1)  // consider only active APs
        {
            AP_TxTime = calculateTxTimeForAP(i);

            // track if the new TxTime in maximum
            if(AP_TxTime > maxTxTime)
            {
                GlobalMaxTxTimeAP = i;   // Identify the AP with global Max Tx Time here
                maxTxTime = AP_TxTime;
            }
        }
    }

    return maxTxTime;
}

void calculateTotalSpeedAmongAPs()
{
    float totalSpeedRAP, totalSpeedVAP, totalSpeedMAP, AP_TxTimeRAP, AP_TxTimeVAP, AP_TxTimeMAP, RAP_Speed, VAP_Speed, MAP_Speed;
    totalSpeedRAP = 0.0;
    totalSpeedVAP = 0.0;
    totalSpeedMAP = 0.0;
    RAP_Speed = 0.0;
    VAP_Speed = 0.0;
    MAP_Speed = 0.0;

    float rsp, vsp, msp,tsp,tsp_rap = 0.0, tsp_vap = 0.0, tsp_map = 0.0;
    for(int i=0; i<NoAP; i++)
    {
        if(AIActive[i].ifActive == 1 && AIActive[i].type ==0)
        {
            AP_TxTimeRAP = calculateTxTimeForAP(i);
            if(AP_TxTimeRAP == 0.0)
            continue;
            RAP_Speed = 1.0/AP_TxTimeRAP;
            rsp = RAP_Speed * AIActive[i].NoConHost;
            tsp_rap = tsp_rap+rsp;
            totalSpeedRAP = totalSpeedRAP + RAP_Speed;
        }
        else if(AIActive[i].ifActive == 1 && AIActive[i].type ==1)
        {
            AP_TxTimeVAP = calculateTxTimeForAP(i);
            if(AP_TxTimeVAP == 0.0)
            continue;
            VAP_Speed = 1.0/AP_TxTimeVAP;
            vsp = VAP_Speed * AIActive[i].NoConHost;
            tsp_vap = tsp_vap+vsp;
            totalSpeedVAP = totalSpeedVAP + VAP_Speed;
        }
        else if(AIActive[i].ifActive == 1 && AIActive[i].type == 2)
        {
            AP_TxTimeMAP = calculateTxTimeForAP(i);
            if(AP_TxTimeMAP == 0.0)
            continue;
            MAP_Speed = 1.0/AP_TxTimeMAP;
            msp = MAP_Speed * AIActive[i].NoConHost;
            tsp_map = tsp_map+ msp;
            totalSpeedMAP = totalSpeedMAP + MAP_Speed;
        }
    }

    tsp = tsp_rap+ tsp_map;
    speedOfRAP = tsp_rap;
    speedOfMAP = tsp_map;
    speedOfAPs = tsp;
}

void calculateInitialAP_HostLinkSpeed()
{
    int x = 5;
    float distanceBtwAP_Host=0.0;
    double tempLinkSpeed,tempLinkSpeed2g,tempLinkSpeed5g;
    int pnew=0;


//2.4Ghz Estimation
    for(int i=0;i<NoAP;i=i+2)
    {
        for(int j=0;j<NoHost;j++)
        {
            distanceBtwAP_Host = sqrt(pow((AI[i].PositionX/x-HI[j].PositionX/x),2)+
                                      pow((AI[i].PositionY/x-HI[j].PositionY/x),2));


               // AP_HostLinkSpeed[i][j] = adjustedRatio * LinkSpeedEstimationFunction(distanceBtwAP_Host);

               double sigST2g = pathLossModel(i,j);
              // printf("2sigST2g=%f\n",sigST2g);
               tempLinkSpeed2g = adjustedRatio * trans_speed(sigST2g);
               //printf("tempLinkSpeed2g=%f\n",tempLinkSpeed2g);
                //AP_HostLinkSpeed2g[i][j]=tempLinkSpeed2g;
                AP_HostLinkSpeed[i][j]=tempLinkSpeed2g;
    // printf("AP_HostLinkSpeed2g[%d][%d]=%f\n",i,j,AP_HostLinkSpeed2g[i][j]);
            //AP_HostLinkSpeed[i][j] = AP_HostLinkSpeed[i][j] * pow((1.0 - (float)LINK_SPEED_DROP_PER_WALL/100),NoOfWallsBtwHostAPPair[j][i]);
        }
     }
     // 5Ghz Estimation

     for(int i=1;i<NoAP;i=i+2)
    {
        for(int j=0;j<NoHost;j++)
        {
            distanceBtwAP_Host = sqrt(pow((AI[i].PositionX/x-HI[j].PositionX/x),2)+
                                      pow((AI[i].PositionY/x-HI[j].PositionY/x),2));


               // AP_HostLinkSpeed[i][j] = adjustedRatio * LinkSpeedEstimationFunction(distanceBtwAP_Host);

               double sigST5g = pathLossModel5g(i,j);
               //printf("5sigST5g=%f\n",sigST5g);
               tempLinkSpeed5g = adjustedRatio * trans_speed5g(sigST5g);
//printf("tempLinkSpeed5g=%f\n",tempLinkSpeed5g);
               // AP_HostLinkSpeed5g[i][j]=tempLinkSpeed5g;
                AP_HostLinkSpeed[i][j]=tempLinkSpeed5g;
// printf("%d-5g[%d][%d]=%f\n",++pnew,i,j,AP_HostLinkSpeed5g[i][j]);
            //AP_HostLinkSpeed[i][j] = AP_HostLinkSpeed[i][j] * pow((1.0 - (float)LINK_SPEED_DROP_PER_WALL/100),NoOfWallsBtwHostAPPair[j][i]);
        }
    }

   // exit(1);
   FILE *fpri;
    fpri=fopen("AllResult.txt", "w");
         for(int i=0;i<NoAP;i++)
         {
         for(int j=0;j<NoHost;j++)
         { //if(i==0 || i%2==0)
            // AP_HostLinkSpeed[i][j]=AP_HostLinkSpeed5g[i][j];
            //else
           // AP_HostLinkSpeed[i][j]=AP_HostLinkSpeed2g[i][j];
         //printf("AP_HostLinkSpeed[%d][%d]=%f\n",i,j,AP_HostLinkSpeed[i][j]);
         fprintf(fpri, "AP_HostLinkSpeed[%d][%d]=%f ", i,j,AP_HostLinkSpeed[i][j]);
        fprintf(fpri, "\n");
         }
         }
    fclose(fpri);
          /*FILE *fpri;
    fpri=fopen("Result.txt", "w");
    for(int i= 0; i<NoHost; i++){
    for(int j= 0; j<NoAP; j++) {
        fprintf(fpri, "%f ", AP_HostLinkSpeed[i][j]);
        fprintf(fpri, "\n");
    }
    }
    fclose(fpri);*/
//exit(1);
}


float LinkSpeedEstimationFunction(float distanceBtwAP_Host)
{
    float LinkSpeed;
    if (distanceBtwAP_Host == 0.0) {
      LinkSpeed = 120.0;
    }
    else if (distanceBtwAP_Host > 0.0 && distanceBtwAP_Host < 40.0) {
      LinkSpeed = -0.0022 * distanceBtwAP_Host * distanceBtwAP_Host * distanceBtwAP_Host
	+ 0.1853 * distanceBtwAP_Host * distanceBtwAP_Host - 5.3348 * distanceBtwAP_Host + 117.43;
    }
    else if (distanceBtwAP_Host >= 40.0 && distanceBtwAP_Host < 75.0) {
      LinkSpeed = -0.00006 * distanceBtwAP_Host * distanceBtwAP_Host * distanceBtwAP_Host
	+ 0.0095 * distanceBtwAP_Host * distanceBtwAP_Host - 1.732 * distanceBtwAP_Host + 117.17;
    }
    else if (distanceBtwAP_Host >= 75.0 && distanceBtwAP_Host < 100.0) {
      LinkSpeed = 0.000438 * distanceBtwAP_Host * distanceBtwAP_Host * distanceBtwAP_Host
	- 0.10955 * distanceBtwAP_Host * distanceBtwAP_Host + 8.477156 * distanceBtwAP_Host -189.481818;
    }
    else {
      LinkSpeed =  1.0;
    }

    return LinkSpeed;

}

float calculateSumOfAllLinkSpeed()
{
    float sum =0;

    for(int m=0; m<NoHost; m++)
    {
        sum = sum + HIActive[m].AssocAP_HostLinkSpeed;
    }

    return sum;
}

float calculateLinkSpeedCostFunction()
{
    float E = 0.0, F;

    for(int i=0; i<NoAP; i++)
    {
        F = 0.0;
        if(AIActive[i].ifActive == 1)
        {
            for(int j=0;j<AIActive[i].NoConHost;j++)
            {
                F = F + (1.0 / (HIActive[AIActive[i].ConHost[j]-1].AssocAP_HostLinkSpeed) );
            }
        }

        E = E + pow(F,3);
    }

    return E;
}




void inputChannelIDforActiveAPs()
{
    strcpy(ipChannelIDFileName, "inputChannelID_");
    strcat(ipChannelIDFileName,ipFileNamePart);
    strcat(ipChannelIDFileName,".txt");

    FILE *ChannelIDFile;

    if((ChannelIDFile = fopen(ipChannelIDFileName,"rt")) == NULL)   // Check if a file for channel ID is not found
    {
        for(int i=0; i<NoAP; i++)
        {
            if(AIActive[i].ifActive == 1)
            {
                //printf("%d\t",i+1);
            }
        }

        ChannelIDFile = fopen(ipChannelIDFileName,"wt");            // Make a new file for saving the channel ID inputs

        //printf("\n\nPlease input <-\n");
        for(int i=0; i<NoAP; i++)
        {
            if(AIActive[i].ifActive == 1)
            {
                //printf("Channel # for AP %d : ",i+1) ;
                scanf("%d",&AIActive[i].ChannelID);
                fprintf(ChannelIDFile,"%d\n",AIActive[i].ChannelID);
            }
        }
        fclose(ChannelIDFile);
    }
    else
    {
        for(int i=0; i<NoAP; i++)
        {
            if(AIActive[i].ifActive == 1)
            {
                fscanf(ChannelIDFile,"%d",&AIActive[i].ChannelID);
            }
        }

        fclose(ChannelIDFile);
    }

}



int ifCurrentlySwappable(int HA, int HB)    // HA, HB: index of swapping candidate hosts (index starts from 0)
{
    int swapFlag = 0;
    if(HIActive[HB].AssocAP != HIActive[HA].AssocAP) // if they are associated to the same AP, then not swappable
    {
        // Check if each host includes the other's associated AP in its associable APs list

        for(int m=0;m<HIActive[HA].NoConAP;m++)
        {
            if(HIActive[HA].ConAP[m]==HIActive[HB].AssocAP)
            {
                //printf("--Check--\n");
                swapFlag = 1;
                break;
            }
        }

        if(swapFlag == 1)
        {
            for(int n=0;n<HIActive[HB].NoConAP;n++)
            {
                if(HIActive[HB].ConAP[n]==HIActive[HA].AssocAP)
                {
                    swapFlag = 2;
                    //printf("--Check--\n");
                    break;
                }
            }
        }
    }

    if(swapFlag == 2) return 1;

    else return 0;
}


float distance(float x_1,float y_1,float x_2,float y_2)
 {
        int x = 1;
       float distance=0.0;

       distance=sqrt(pow((x_2/x-x_1/x),2)+pow((y_2/x-y_1/x),2));

       return distance;
    }


char* substring(const char* str, size_t begin, size_t len)
{

  if (str == 0 || strlen(str) == 0 || strlen(str) < begin || strlen(str) < (begin+len))
    return 0;

  return strndup(str + begin, len);
}



void printOutput(char *opFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    FILE *opfp;
    opfp = fopen(opFileName,"wt");
    float sumDistance, sumLinkSpeed, tempDistance, tempLinkSpeed, sumTxTime;

    fprintf(opfp, "AP: List of Host : sumDistance  sumLinkSpeed  TotalTxTime\n");
    for(int i=0; i<NoAP; i++)
        {

            fprintf(opfp, "%d(%d,%d): ",localAIActive[i].APID,(int)localAIActive[i].PositionX, (int)localAIActive[i].PositionY);

            sumDistance = 0.0;
            sumLinkSpeed = 0.0;
            sumTxTime = 0.0;
            for(int j=0; j<localAIActive[i].NoConHost; j++)
            {

                if(localAIActive[i].ifActive == 1)  fprintf(opfp, "%d ",localAIActive[i].ConHost[j]);
                tempDistance = distance(localHIActive[localAIActive[i].ConHost[j]-1].PositionX, localHIActive[localAIActive[i].ConHost[j]-1].PositionY, localAIActive[i].PositionX, localAIActive[i].PositionY);
                tempLinkSpeed = AP_HostLinkSpeed[i][localAIActive[i].ConHost[j]-1];
                //calculateAP_HostLinkSpeed(tempDistance);

                sumDistance = sumDistance + tempDistance;
                sumLinkSpeed = sumLinkSpeed + tempLinkSpeed;
                //*** sumTxTime = sumTxTime + 1/ tempLinkSpeed; // updated in Version 18
            }
// updated in Version 18
            sumTxTime = calculateTxTimeForAP(i);

            if(localAIActive[i].ifActive == 1)   fprintf(opfp, ": %f\t%f\t%f\n",sumDistance,sumLinkSpeed, sumTxTime);
            fprintf(opfp, "\n");
        }


//mamun
    fprintf(opfp, "\n");

    fprintf(opfp, "Host: AssocAP : Associable APs: Distance  LinkSpeed  TxTime\n");
    for(int i=0;i<NoHost;i++)
    {
        tempDistance = distance(localHIActive[i].PositionX, localHIActive[i].PositionY, localAIActive[localHIActive[i].AssocAP-1].PositionX, localAIActive[localHIActive[i].AssocAP-1].PositionY);
        tempLinkSpeed = AP_HostLinkSpeed[localHIActive[i].AssocAP-1][i];
        //calculateAP_HostLinkSpeed(tempDistance);
        //fprintf(opfp, "%d  : %d : %f\t%f\t%f\n", i+1, localHIActive[i].AssocAP, tempDistance, tempLinkSpeed, 1/tempLinkSpeed);
        fprintf(opfp, "%d  : %d : ", localHIActive[i].HostID, localHIActive[i].AssocAP);
        for(int j=0;j<localHIActive[i].NoConAP;j++)     fprintf(opfp, "%d  ", localHIActive[i].ConAP[j]);
        //*** fprintf(opfp, ": %f\t%f\t%f\n", tempDistance, tempLinkSpeed, 1/tempLinkSpeed);
// updated in Version 18
        fprintf(opfp, ": %f\t%f\t%f\n", tempDistance, tempLinkSpeed, localHIActive[i].HostActiveRate/tempLinkSpeed);
    }


    // Printing output by considering node ID

    fprintf(opfp, "\n\n\n");


    for(int i=0; i<NoAP; i++)
    {
        if(localAIActive[i].ifActive == 1)
        {
            fprintf(opfp, "%d - %d:\t\t",localAIActive[i].nodeID,localAIActive[i].APID);
            for(int j=0;j<localAIActive[i].NoConHost;j++)
            {
                fprintf(opfp, "%d \t",localHIActive[localAIActive[i].ConHost[j]-1].nodeID);
            }
            fprintf(opfp, "\n");
        }
    }

    fprintf(opfp, "\n\n");
    for(int i=0;i<NoHost;i++)
    {
        fprintf(opfp, "%d - %d:\t\t%d \n",localHIActive[i].nodeID, localHIActive[i].HostID, localAIActive[localHIActive[i].AssocAP-1].nodeID);
    }




    if(failureFlag == 2)
    {
        fprintf(opfp, "\n\nfailure!!\n\n");
    }





    fclose(opfp);

}


void prepareInputFileForPerlProgramToDrawAssociation(char *DrawAssociationInputFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    int noOfActiveAp;

    noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)
        if (localAIActive[i].ifActive == 1)
            {
                localAIActive[i].nodeID = noOfActiveAp;
                noOfActiveAp++;
            }

    FILE *DrawAssociationInput;

    DrawAssociationInput = fopen(DrawAssociationInputFileName,"wt");

    fprintf(DrawAssociationInput, "%d %d\n",gridSizeX*gridScale,gridSizeY*gridScale);
    fprintf(DrawAssociationInput, "%d\n",noOfActiveAp);
    for(int i=0; i<NoAP; i++)
    {
        if(localAIActive[i].ifActive == 1)
        {
            fprintf(DrawAssociationInput, "%d %d %d %.2f %.2f %d\n",localAIActive[i].nodeID,localAIActive[i].APID,localAIActive[i].GroupID,localAIActive[i].PositionX, localAIActive[i].PositionY,localAIActive[i].ChannelID);
        }
    }

    fprintf(DrawAssociationInput, "%d\n",NoHost);
    for(int j=0; j<NoHost; j++)
    {

        fprintf(DrawAssociationInput, "%d %d %d %.2f %.2f %.2f\n",localHIActive[j].HostID,localAIActive[localHIActive[j].AssocAP-1].nodeID, localHIActive[j].GroupID, localHIActive[j].PositionX, localHIActive[j].PositionY, localHIActive[j].HostActiveRate);
    }

    fclose(DrawAssociationInput);
}

void prepareInputFileForSimulatorInputGenerator(char *SimulatorInputGeneratorFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    int noOfActiveAp;

    noOfActiveAp = 0;
    for(int i=0; i<NoAP; i++)
        {
        if(localAIActive[i].participateInSelection == 0)
            continue;
        if(localAIActive[i].NoConHost == 0)
            continue;
        if (localAIActive[i].ifActive == 1)
            {
                localAIActive[i].nodeID = noOfActiveAp;
                noOfActiveAp++;
            }

        }

    for (int i=0; i<NoHost; i++)
    {
        localHIActive[i].nodeID = noOfActiveAp+i;    // *** Assign Node ID for Hosts here
    }



    FILE *SimIPGenInput;
    int q=1;// 1=ac
    int p=0;// 0=n

    SimIPGenInput = fopen(SimulatorInputGeneratorFileName,"wt");

    fprintf(SimIPGenInput, "%d\t%d\n%d\n%.1f\n",gridSizeX,gridSizeY,gridScale,APCoverageRm);

    fprintf(SimIPGenInput, "\n%d\n%d\n",noOfActiveAp,NoHost);
    int klm =0;
    for(int i=0; i<NoAP; i++)
    {
    if(localAIActive[i].participateInSelection == 0)
            continue;
        if(localAIActive[i].ifActive == 1 && localAIActive[i].NoConHost != 0)
        {
            fprintf(SimIPGenInput, "%d\t%d\t%d\t%d\t%f\t%f\t%d\t",localAIActive[i].APID,localAIActive[i].nodeID, localAIActive[i].GroupID ,localAIActive[i].ChannelID,localAIActive[i].PositionX, localAIActive[i].PositionY,localAIActive[i].type);
           if( (localAIActive[i].APID)%2==0)
             fprintf(SimIPGenInput,"%d\t\n",q);
             else
           fprintf(SimIPGenInput,"%d\t\n",p);
        }
    }

    fprintf(SimIPGenInput, "\n");

    for(int j=0; j<NoHost; j++)
    {

        fprintf(SimIPGenInput, "\n%d\t%d\t%d\t%d\t%f\t%f\t%f",localHIActive[j].HostID,localHIActive[j].nodeID, localHIActive[j].GroupID , localAIActive[localHIActive[j].AssocAP-1].nodeID,
                localHIActive[j].PositionX, localHIActive[j].PositionY, localHIActive[j].HostActiveRate);

        fprintf(SimIPGenInput, "\t%d",localHIActive[j].NoConAP);
        for(int k=0;k<localHIActive[j].NoConAP; k++)    fprintf(SimIPGenInput, "\t%d",localAIActive[localHIActive[j].ConAP[k]-1].nodeID);
    }


    fprintf(SimIPGenInput, "\n%d\n",LINK_SPEED_DROP_PER_WALL);

    //fprintf(SimIPGenInput, "\n%d", NoOfWalls);
    //for (int i=0;i<NoOfWalls;i++)  fprintf(SimIPGenInput, "\n%f %f %f %f", Walls[i].start_x, Walls[i].start_y, Walls[i].end_x, Walls[i].end_y);

    fclose(SimIPGenInput);

}


void generateFIELD_File(char *FIELD_infoFileName)
{
    // *** Start of Field_Size file

    FILE *FIELD_size;

    FIELD_size = fopen(FIELD_infoFileName,"wt");

    fprintf(FIELD_size, "%d\t%d",gridSizeX*gridScale,gridSizeY*gridScale);

    fclose(FIELD_size);
    // *** End of FIELD_info file
}


void generateNIC_File(char *NIC_infoFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    // *** Start of NIC_info file
    FILE *NIC_info;

    NIC_info = fopen(NIC_infoFileName,"wt");


    for(int i=0; i<NoAP; i++)
        {
            if(localAIActive[i].ifActive == 1)
            {
                fprintf(NIC_info, "%d\t0\t%d\tn\t4\t%0.1f\n",localAIActive[i].nodeID,localAIActive[i].ChannelID,APCoverageRm);
            }
        }

    for(int j=0; j<NoHost; j++)
    {

        fprintf(NIC_info, "%d\t0\t%d\tn\t4\t%0.1f\n",localHIActive[j].nodeID,localAIActive[localHIActive[j].AssocAP-1].ChannelID,APCoverageRm);
    }

    fclose(NIC_info);
    // *** End of NIC_info file
}


void generateNODE_File(char *NODE_infoFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    // *** Start of node_info file

    FILE *NODE_info;

    NODE_info = fopen(NODE_infoFileName,"wt");

    //fprintf(NODE_info, "%d\n",noOfActiveAp);
    for(int i=0; i<NoAP; i++)
    {
         if(localAIActive[i].ifActive == 1) fprintf(NODE_info, "%d\t%d\t%d\tG\t%d\n", localAIActive[i].nodeID, (int)localAIActive[i].PositionX, (int)localAIActive[i].PositionY,localAIActive[i].type);
    }

    for(int j=0; j<NoHost; j++)
    {
        fprintf(NODE_info, "%d\t%d\t%d\tH\t-5\n",localHIActive[j].nodeID, (int)localHIActive[j].PositionX, (int)localHIActive[j].PositionY);
    }

    fclose(NODE_info);
    // *** End of NODE_info file

}

void generateNODE_File1(char *NODE_infoFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    // *** Start of node_info file

    FILE *NODE_info;

    NODE_info = fopen(NODE_infoFileName,"wt");

    //fprintf(NODE_info, "%d\n",noOfActiveAp);
    for(int i=0; i<NoAP; i++)
    {
         if(localAIActive[i].ifActive == 1) fprintf(NODE_info, "%d\t%d\t%d\tG\n", localAIActive[i].nodeID, (int)localAIActive[i].PositionX, (int)localAIActive[i].PositionY);
    }

    for(int j=0; j<NoHost; j++)
    {
        fprintf(NODE_info, "%d\t%d\t%d\tH\n",localHIActive[j].nodeID, (int)localHIActive[j].PositionX, (int)localHIActive[j].PositionY);
    }

    fclose(NODE_info);
    // *** End of NODE_info file

}


void generateROUTE_File(char *ROUTE_infoFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    // *** Start of ROUTE_info file

    FILE *ROUTE_info;

    ROUTE_info = fopen(ROUTE_infoFileName,"wt");

    fprintf(ROUTE_info, "%d\n",NoHost*2);

    for(int j=0; j<NoHost; j++)
    {
        fprintf(ROUTE_info, "2\t%d\t%d\n",localHIActive[j].nodeID, localAIActive[localHIActive[j].AssocAP-1].nodeID);
        fprintf(ROUTE_info, "2\t%d\t%d\n",localAIActive[localHIActive[j].AssocAP-1].nodeID, localHIActive[j].nodeID);
    }

    fclose(ROUTE_info);
    // *** End of ROUTE_info file

}


void generateSAP_File(char *SAP_patternFileName, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
    // *** Start of SAP_pattern file

    FILE *SAP_pattern;


    SAP_pattern = fopen(SAP_patternFileName,"wt");

    for( int i=0; i<NoAP; i++)
    {
        if(localAIActive[i].ifActive == 1) fprintf(SAP_pattern, "%d\ts\n",localAIActive[i].nodeID);
    }

    for(int j=0; j<NoHost; j++)
    {
        fprintf(SAP_pattern, "%d\ts\n",localHIActive[j].nodeID);
    }

    fclose(SAP_pattern);
    // *** End of SAP_pattern file
}

// mn4

void generateAdjustmentSpeed(const char *speedFile, int ifAdj, float T_BW, float T_S)
{

FILE * spa;
spa = fopen(speedFile,"wt");

fprintf(spa, "%d\t%f\t%f",ifAdj, T_BW, T_S);


}

void generateFinalOPF(const char *finalOPF, struct APInfo *localAIActive, struct HostInfo *localHIActive)
{
  FILE *sp;

    float txtmp, fnlthpt;

    sp = fopen(finalOPF,"wt");
    int cnt = 0, r_ap = 0 , v_ap = 0 , m_ap = 0;

    for( int i=0; i<NoAP; i++)
    {
        if(localAIActive[i].ifActive == 1)
        {
        cnt++;
        if(localAIActive[i].type == 0)
            {
            r_ap++;
            }
        else if(localAIActive[i].type == 1)
            {
            v_ap++;
            }
        else if(localAIActive[i].type == 2)
            {
            m_ap++;
            }
        }

    }
    printf("fnlThroughputuuuuuuuuuuuuuuuuu=%f\n",fnlThroughput);

    fnlthpt = fnlThroughput * adjustedRatio;
    fprintf(sp, "%d\t%d\t%d\t%d\t%f\t%f\t%f\t%f\t\%f\n",cnt,r_ap,v_ap,m_ap,fnlThroughput,fnlthpt,speedOfAPs, speedOfRAP, speedOfMAP);


    fclose(sp);

}

