#include <stdio.h>
#include <stdlib.h>

typedef struct
{
    int *w; // neighbours list: if w[j]=1, node i linked to j.
    int k; // node degree
    double theta; // phase of the oscilator
    double omega; // angular velocity of the oscilator
    double own_f;
} Node; //

#define N 100000
#define space 6

int main(int argc, const char** argv) {

    Node *network_now;


    network_now= (Node*) malloc (N*sizeof(Node));


    for(int i=0; i<N; i++)
    {
        network_now[i].w = (int*)malloc(space*sizeof(int));
    }

    for(int i=0; i<N; i++)//initialize degree of each node to 0
    {
        network_now[i].k=0.0;

        for(int j=i; j<N; j++)
        {
            //printf("Nodo: %i\n", j);
            network_now[i].w[j]=0.0;
            network_now[j].w[i]=0.0;
        }
    }


    printf("%s", "Duck");
    return 0;
}