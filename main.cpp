#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <cmath>
#include <fstream>
#include <math.h>


using namespace std;

class Configuration
{
public:
    double permeability;
    double sigma;
    double k_active;
    double k_conf;
    double eta;
    double landa;
    double IFR;
    double mu;
    double xi;
    int simulation_time;
    int quarentine_step_time;
    double p_active;

    Configuration(string file_name = "configuracion.txt"){
        FILE *F;
        unsigned int Fsize;
        char *Fcopy;

        F = fopen(file_name.c_str(), "rt");

        fseek(F, 0, SEEK_END);
        Fsize = ftell(F);
        rewind(F);

        Fcopy = (char *)malloc(sizeof(char) * Fsize);
        fread(Fcopy, 1, Fsize, F);
        fclose(F);

        char *p;
        char s[25];

        strcpy(s, "permeability=");
        p = strstr(Fcopy, s);
        permeability = atof(p + strlen(s));

        strcpy(s, "sigma=");
        p = strstr(Fcopy, s);
        sigma = atof(p + strlen(s));

        strcpy(s, "k_active=");
        p = strstr(Fcopy, s);
        k_active = atof(p + strlen(s));

        strcpy(s, "k_conf=");
        p = strstr(Fcopy, s);
        k_conf = atof(p + strlen(s));

        strcpy(s, "eta=");
        p = strstr(Fcopy, s);
        eta = atof(p + strlen(s));

        strcpy(s, "landa=");
        p = strstr(Fcopy, s);
        landa = atof(p + strlen(s));

        strcpy(s, "IFR=");
        p = strstr(Fcopy, s);
        IFR = atof(p + strlen(s));

        strcpy(s, "mu=");
        p = strstr(Fcopy, s);
        mu = atof(p + strlen(s));

        strcpy(s, "xi=");
        p = strstr(Fcopy, s);
        xi = atof(p + strlen(s));

        strcpy(s, "quarentine_step_time=");
        p = strstr(Fcopy, s);
        quarentine_step_time = atof(p + strlen(s));

        strcpy(s, "simulation_time=");
        p = strstr(Fcopy, s);
        simulation_time = atoi(p + strlen(s));

        strcpy(s, "p_active=");
        p = strstr(Fcopy, s);
        p_active = atof(p + strlen(s));


    }
};


double step_function(Configuration &C, int t){
    if (t <= C.quarentine_step_time) return 1.;
    else return C.p_active;
}


class Simulation
{
public:
    Configuration Config;
    double susceptible, secure_home, exposed, infected, recovered, pending_death, dead;
    int t=0;


    Simulation(Configuration C){
        Config = C;
        ofstream outfile("data.txt",  ios::out);
    }

    void initial_state(double s, double sh, double e, double i, double r, double pd, double d){
        this->susceptible = s;
        this->secure_home = sh;
        this->exposed = e;
        this->infected = i;
        this->recovered = r;
        this->pending_death = pd;
        this->dead = d;
    }

    void initial_state(string file_name = "initial_state.txt"){
        FILE *F;
        unsigned int Fsize;
        char *Fcopy;

        F = fopen(file_name.c_str(), "rt");

        fseek(F, 0, SEEK_END);
        Fsize = ftell(F);
        rewind(F);

        Fcopy = (char *)malloc(sizeof(char) * Fsize);
        fread(Fcopy, 1, Fsize, F);
        fclose(F);

        char *p;
        char s[25];

        strcpy(s, "s=");
        p = strstr(Fcopy, s);
        this->susceptible = atof(p + strlen(s));

        strcpy(s, "sh=");
        p = strstr(Fcopy, s);
        this->secure_home = atof(p + strlen(s));

        strcpy(s, "e=");
        p = strstr(Fcopy, s);
        this->exposed = atof(p + strlen(s));

        strcpy(s, "i=");
        p = strstr(Fcopy, s);
        this->infected = atof(p + strlen(s));

        strcpy(s, "pd=");
        p = strstr(Fcopy, s);
        this->pending_death = atof(p + strlen(s));

        strcpy(s, "d=");
        p = strstr(Fcopy, s);
        this->dead = atof(p + strlen(s));

        strcpy(s, "r=");
        p = strstr(Fcopy, s);
        this->recovered = atof(p + strlen(s));
    }


    void update_probabilities(){
        // TODO: step funcition que se pueda pasar como input? quizá?
        this->P_active = step_function(this->Config, this->t);
        this->P_infection = this->_P_infection();
        this->P_home_is_secure = this->_P_home_is_secure();
        this->P_secure_in_home = this->_P_secure_in_home();
    }


    void evolve(){
        this->t += 1;
        this->update_probabilities();

        double S = this->secure_home + this->susceptible;

        secure_home = S * this->P_secure_in_home;
        susceptible = S * (1 - this->P_secure_in_home) * (1 - this->P_infection);

        dead = this->pending_death * this->Config.xi;
        recovered = this->Config.IFR * (1 - this->Config.mu) * this->infected;
        pending_death = this->Config.IFR * this->Config.mu * this->infected + this->pending_death * (1 - this->Config.xi);

        infected = this->exposed * this->Config.eta + this->infected * (1 - this->Config.IFR);

        exposed = S * (1 - this->P_secure_in_home) * this->P_infection + this->exposed * (1 - this->Config.eta);
    }

    int save_state(){
        ofstream outfile("data.txt",  ios::out | ios::app);

        if (!outfile.is_open()){
            cout << "Error al crear el fichero de guardado datos" << endl;
            return 0;
        }
        
        outfile << this->t << "\t" << this->secure_home << "\t" << this->susceptible << "\t" << this->exposed << "\t" << this->infected << "\t" << this->pending_death << "\t" << this->dead << "\t" << this->recovered <<endl;
           
        outfile.close();

        return 1;
    }





private:
    double P_active;
    double P_home_is_secure;
    double P_secure_in_home;
    double P_not_successful_infection;
    double P_active_infections;
    double P_conf_infections;
    double P_infection;

    double _P_home_is_secure(){
        return pow((1 - infected), Config.sigma - 1);
    }

    double _P_secure_in_home(){
        return (1 - P_active) * _P_home_is_secure() * (1 - Config.permeability);
    }

    double _P_infection(){
        P_not_successful_infection = 1 - Config.landa * infected;

        P_active_infections = P_active * (
            1 - pow(P_not_successful_infection, Config.k_active)
        );
        P_conf_infections = (1 - P_active) * (
            1 - pow(P_not_successful_infection, Config.k_conf)
        );

        return P_active_infections + P_conf_infections;
    }

};


int main()
{
    Configuration Config("configuracion.txt");

    Simulation Simul(Config);

    Simul.initial_state();

    for(int i=0; i < Config.simulation_time; i++){
        Simul.evolve();
        Simul.save_state();
    }
    return 1;
}