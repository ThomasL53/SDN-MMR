def generate_segment_url(ip1, ip2, num_lines):
    with open("output.xml", "w") as file:
        for i in range(1, num_lines + 1):
            ip_address = ip1 if i % 2 == 1 else ip2
            line = f'<SegmentURL media="http://{ip_address}/video/video_720_dash{i}.m4s" />\n'
            file.write(line)

# Générer le fichier avec les lignes spécifiées
#Params: ip serveur 1, ip serveur 2, nombre de chunk à jouer
generate_segment_url("192.168.1.1", "192.168.1.2", 101)